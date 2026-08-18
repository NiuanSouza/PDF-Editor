import io
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import pikepdf


@csrf_exempt
@require_http_methods(["POST"])
def merge_pdfs(request):
    """
    Recebe múltiplos arquivos PDF via multipart/form-data (campo 'files')
    e retorna o PDF mesclado como download.
    """
    files = request.FILES.getlist('files')

    if len(files) < 2:
        return JsonResponse(
            {'error': 'Envie pelo menos 2 arquivos PDF para juntar.'},
            status=400
        )

    # Validar que todos são PDFs
    for f in files:
        if f.content_type != 'application/pdf' and not f.name.lower().endswith('.pdf'):
            return JsonResponse(
                {'error': f'O arquivo "{f.name}" não é um PDF válido.'},
                status=400
            )

    # Registrar auditoria
    audit_log = None
    try:
        from apps.audit.models import AuditLog
        audit_log = AuditLog.objects.create(
            tool_used='merge',
            ip_address=_get_client_ip(request),
            file_count=len(files),
            status='PROCESSING',
        )
    except Exception:
        pass  # Auditoria não deve bloquear o processamento

    try:
        merged = pikepdf.Pdf.new()

        for uploaded_file in files:
            file_bytes = uploaded_file.read()
            src = pikepdf.Pdf.open(io.BytesIO(file_bytes))
            merged.pages.extend(src.pages)

        output_buffer = io.BytesIO()
        merged.save(output_buffer)
        output_buffer.seek(0)

        # Atualizar auditoria como concluída
        if audit_log:
            try:
                audit_log.status = 'COMPLETED'
                audit_log.completed_at = timezone.now()
                audit_log.save()
            except Exception:
                pass

        response = HttpResponse(
            output_buffer.read(),
            content_type='application/pdf',
        )
        response['Content-Disposition'] = 'attachment; filename="merged.pdf"'
        return response

    except pikepdf.PdfError as e:
        if audit_log:
            try:
                audit_log.status = 'FAILED'
                audit_log.error_message = str(e)
                audit_log.completed_at = timezone.now()
                audit_log.save()
            except Exception:
                pass
        return JsonResponse(
            {'error': f'Erro ao processar PDF: {str(e)}'},
            status=422
        )
    except Exception as e:
        if audit_log:
            try:
                audit_log.status = 'FAILED'
                audit_log.error_message = str(e)
                audit_log.completed_at = timezone.now()
                audit_log.save()
            except Exception:
                pass
        return JsonResponse(
            {'error': 'Erro interno ao juntar os PDFs. Tente novamente.'},
            status=500
        )


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
