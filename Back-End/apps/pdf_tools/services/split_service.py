import io
import re
import zipfile
import pikepdf


class SplitService:
    @staticmethod
    def parse_page_ranges(range_str, total_pages):
        """
        Interpreta strings como '1-3, 5, 7-9' e retorna uma lista ordenada de índices 0-based.
        """
        selected = set()
        parts = [p.strip() for p in range_str.split(',') if p.strip()]

        for part in parts:
            if '-' in part:
                match = re.match(r'^(\d+)\s*-\s*(\d+)$', part)
                if not match:
                    raise ValueError(f'Intervalo inválido: "{part}"')
                start, end = int(match.group(1)), int(match.group(2))
                if start > end:
                    start, end = end, start
                for p in range(start, end + 1):
                    if 1 <= p <= total_pages:
                        selected.add(p - 1)
            else:
                if not part.isdigit():
                    raise ValueError(f'Número de página inválido: "{part}"')
                p = int(part)
                if 1 <= p <= total_pages:
                    selected.add(p - 1)

        if not selected:
            raise ValueError('Nenhuma página válida foi selecionada no intervalo.')

        return sorted(list(selected))

    @classmethod
    def split(cls, file_bytes, mode='all', page_range=''):
        """
        Divide um arquivo PDF.
        :param file_bytes: bytes do PDF original
        :param mode: 'all' para extrair todas as páginas em ZIP, ou 'range' para extrair um intervalo em 1 PDF
        :param page_range: string de intervalo (ex: '1-3, 5') quando mode == 'range'
        :return: tupla (bytes_resultado, content_type, filename)
        """
        src = pikepdf.Pdf.open(io.BytesIO(file_bytes))
        total_pages = len(src.pages)

        if total_pages == 0:
            raise ValueError('O arquivo PDF não contém páginas.')

        if mode == 'range':
            if not page_range:
                raise ValueError('Informe o intervalo de páginas desejado (ex: 1-3, 5).')

            selected_indices = cls.parse_page_ranges(page_range, total_pages)
            dst = pikepdf.Pdf.new()
            for idx in selected_indices:
                dst.pages.append(src.pages[idx])

            buf = io.BytesIO()
            dst.save(buf)
            buf.seek(0)
            return buf.getvalue(), 'application/pdf', 'dividido.pdf'

        # Mode 'all': gerar arquivo ZIP com cada página individual
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            num_digits = max(2, len(str(total_pages)))
            for i, page in enumerate(src.pages, start=1):
                single_pdf = pikepdf.Pdf.new()
                single_pdf.pages.append(page)
                page_buf = io.BytesIO()
                single_pdf.save(page_buf)
                page_buf.seek(0)
                page_filename = f'pagina_{str(i).zfill(num_digits)}.pdf'
                zip_file.writestr(page_filename, page_buf.getvalue())

        zip_buffer.seek(0)
        return zip_buffer.getvalue(), 'application/zip', 'paginas_divididas.zip'

