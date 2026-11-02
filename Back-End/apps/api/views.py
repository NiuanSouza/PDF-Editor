import io
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from apps.pdf_tools.services import (
    MergeService,
    SplitService,
    CompressService,
    WordConversionService,
    ImageConversionService,
    SecurityService,
    TransformService,
)


def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _create_audit(tool_name, request, file_count=1):
    try:
        from apps.audit.models import AuditLog
        return AuditLog.objects.create(
            tool_used=tool_name,
            ip_address=_get_client_ip(request),
            file_count=file_count,
            status='PROCESSING',
        )
    except Exception:
        return None


def _complete_audit(audit_log):
    if audit_log:
        try:
            audit_log.status = 'COMPLETED'
            audit_log.completed_at = timezone.now()
            audit_log.save()
        except Exception:
            pass


def _fail_audit(audit_log, error_message):
    if audit_log:
        try:
            audit_log.status = 'FAILED'
            audit_log.error_message = str(error_message)
            audit_log.completed_at = timezone.now()
            audit_log.save()
        except Exception:
            pass


# ─── 1. Juntar PDF ────────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(["POST"])
def merge_pdfs(request):
    files = request.FILES.getlist('files')
    if len(files) < 2:
        return JsonResponse({'error': 'Envie pelo menos 2 arquivos PDF para juntar.'}, status=400)

    for f in files:
        if f.content_type != 'application/pdf' and not f.name.lower().endswith('.pdf'):
            return JsonResponse({'error': f'O arquivo "{f.name}" não é um PDF válido.'}, status=400)

    audit = _create_audit('merge', request, len(files))
    try:
        pdf_bytes = MergeService.merge(files)
        _complete_audit(audit)

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="merged.pdf"'
        return response
    except Exception as e:
        _fail_audit(audit, e)
        return JsonResponse({'error': f'Erro ao juntar PDFs: {str(e)}'}, status=422)


# ─── 2. Dividir PDF ───────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(["POST"])
def split_pdf(request):
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'Selecione um arquivo PDF para dividir.'}, status=400)

    mode = request.POST.get('mode', 'all')  # 'all' ou 'range'
    page_range = request.POST.get('page_range', '')

    audit = _create_audit('split', request, 1)
    try:
        content_bytes, content_type, filename = SplitService.split(
            file.read(), mode=mode, page_range=page_range
        )
        _complete_audit(audit)

        response = HttpResponse(content_bytes, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except ValueError as e:
        _fail_audit(audit, e)
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        _fail_audit(audit, e)
        return JsonResponse({'error': f'Erro ao dividir PDF: {str(e)}'}, status=422)


# ─── 3. Comprimir PDF ─────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(["POST"])
def compress_pdf(request):
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'Selecione um arquivo PDF para comprimir.'}, status=400)

    level = request.POST.get('level', 'recommended')

    audit = _create_audit('compress', request, 1)
    try:
        compressed_bytes = CompressService.compress(file.read(), level=level)
        _complete_audit(audit)

        response = HttpResponse(compressed_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="comprimido.pdf"'
        return response
    except Exception as e:
        _fail_audit(audit, e)
        return JsonResponse({'error': f'Erro ao comprimir PDF: {str(e)}'}, status=422)


# ─── 4. Word para PDF ─────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(["POST"])
def word_to_pdf(request):
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'Selecione um arquivo Word (.docx ou .doc).'}, status=400)

    filename = file.name.lower()
    if not (filename.endswith('.docx') or filename.endswith('.doc') or filename.endswith('.odt') or filename.endswith('.rtf')):
        return JsonResponse({'error': 'O arquivo deve estar no formato Word (.docx, .doc, .odt, .rtf).'}, status=400)

    audit = _create_audit('word_to_pdf', request, 1)
    try:
        pdf_bytes = WordConversionService.docx_to_pdf(file.read(), file.name)
        _complete_audit(audit)

        out_name = f"{filename.rsplit('.', 1)[0]}.pdf"
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{out_name}"'
        return response
    except Exception as e:
        _fail_audit(audit, e)
        return JsonResponse({'error': f'Erro ao converter Word para PDF: {str(e)}'}, status=422)


# ─── 5. PDF para Word ─────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(["POST"])
def pdf_to_word(request):
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'Selecione um arquivo PDF para converter para Word.'}, status=400)

    audit = _create_audit('pdf_to_word', request, 1)
    try:
        docx_bytes = WordConversionService.pdf_to_docx(file.read())
        _complete_audit(audit)

        base_name = file.name.rsplit('.', 1)[0] if '.' in file.name else 'documento'
        response = HttpResponse(
            docx_bytes,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{base_name}.docx"'
        return response
    except Exception as e:
        _fail_audit(audit, e)
        return JsonResponse({'error': f'Erro ao converter PDF para Word: {str(e)}'}, status=422)


# ─── 6. PDF para Imagens ──────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(["POST"])
def pdf_to_images(request):
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'Selecione um arquivo PDF para converter em imagens.'}, status=400)

    img_format = request.POST.get('format', 'jpg')
    dpi = int(request.POST.get('dpi', 150))

    audit = _create_audit('pdf_to_images', request, 1)
    try:
        result_bytes, content_type, filename = ImageConversionService.pdf_to_images(
            file.read(), img_format=img_format, dpi=dpi
        )
        _complete_audit(audit)

        response = HttpResponse(result_bytes, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        _fail_audit(audit, e)
        return JsonResponse({'error': f'Erro ao converter PDF para imagens: {str(e)}'}, status=422)


# ─── 7. Imagens para PDF ──────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(["POST"])
def images_to_pdf(request):
    files = request.FILES.getlist('files')
    if not files:
        return JsonResponse({'error': 'Envie pelo menos 1 imagem para converter para PDF.'}, status=400)

    audit = _create_audit('images_to_pdf', request, len(files))
    try:
        pdf_bytes = ImageConversionService.images_to_pdf(files)
        _complete_audit(audit)

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="imagens_convertidas.pdf"'
        return response
    except Exception as e:
        _fail_audit(audit, e)
        return JsonResponse({'error': f'Erro ao converter imagens para PDF: {str(e)}'}, status=422)


# ─── 8. Proteger PDF ──────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(["POST"])
def protect_pdf(request):
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'Selecione um arquivo PDF para proteger.'}, status=400)

    password = request.POST.get('password', '').strip()
    if not password:
        return JsonResponse({'error': 'Informe uma senha para proteger o documento.'}, status=400)

    audit = _create_audit('protect', request, 1)
    try:
        protected_bytes = SecurityService.protect(file.read(), user_password=password)
        _complete_audit(audit)

        response = HttpResponse(protected_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="protegido.pdf"'
        return response
    except Exception as e:
        _fail_audit(audit, e)
        return JsonResponse({'error': f'Erro ao proteger PDF: {str(e)}'}, status=422)


# ─── 9. Desbloquear PDF ───────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(["POST"])
def unlock_pdf(request):
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'Selecione um arquivo PDF para desbloquear.'}, status=400)

    password = request.POST.get('password', '').strip()

    audit = _create_audit('unlock', request, 1)
    try:
        unlocked_bytes = SecurityService.unlock(file.read(), password=password)
        _complete_audit(audit)

        response = HttpResponse(unlocked_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="desbloqueado.pdf"'
        return response
    except ValueError as e:
        _fail_audit(audit, e)
        return JsonResponse({'error': str(e)}, status=401)
    except Exception as e:
        _fail_audit(audit, e)
        return JsonResponse({'error': f'Erro ao desbloquear PDF: {str(e)}'}, status=422)


# ─── 10. Rotacionar PDF ───────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(["POST"])
def rotate_pdf(request):
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'Selecione um arquivo PDF para rotacionar.'}, status=400)

    angle = int(request.POST.get('angle', 90))
    page_selection = request.POST.get('page_selection', 'all')

    audit = _create_audit('rotate', request, 1)
    try:
        rotated_bytes = TransformService.rotate(file.read(), angle=angle, page_selection=page_selection)
        _complete_audit(audit)

        response = HttpResponse(rotated_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="rotacionado.pdf"'
        return response
    except Exception as e:
        _fail_audit(audit, e)
        return JsonResponse({'error': f'Erro ao rotacionar PDF: {str(e)}'}, status=422)


# ─── 11. Marca d'Água ─────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(["POST"])
def watermark_pdf(request):
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'Selecione um arquivo PDF para adicionar marca d\'água.'}, status=400)

    text = request.POST.get('text', '').strip()
    if not text:
        return JsonResponse({'error': 'Informe o texto para a marca d\'água.'}, status=400)

    opacity = float(request.POST.get('opacity', 0.3))
    rotation = float(request.POST.get('rotation', 45))
    font_size = int(request.POST.get('font_size', 42))

    audit = _create_audit('watermark', request, 1)
    try:
        wm_bytes = TransformService.watermark(
            file.read(), text=text, opacity=opacity, rotation=rotation, font_size=font_size
        )
        _complete_audit(audit)

        response = HttpResponse(wm_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="com_marca_dagua.pdf"'
        return response
    except Exception as e:
        _fail_audit(audit, e)
        return JsonResponse({'error': f'Erro ao aplicar marca d\'água: {str(e)}'}, status=422)
