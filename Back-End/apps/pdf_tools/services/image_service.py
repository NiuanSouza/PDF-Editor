import io
import zipfile
from PIL import Image


class ImageConversionService:
    @staticmethod
    def pdf_to_images(file_bytes, img_format='jpg', dpi=150):
        """
        Converte páginas de PDF para imagens (JPG ou PNG).
        :param file_bytes: bytes do PDF original
        :param img_format: 'jpg' ou 'png'
        :param dpi: resolução (ex: 150 para padrão, 300 para alta)
        :return: tupla (bytes_resultado, content_type, filename)
        """
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise RuntimeError('PyMuPDF (fitz) não está instalado no servidor.')

        fmt = img_format.lower()
        if fmt not in ['jpg', 'jpeg', 'png']:
            fmt = 'jpg'
        out_ext = 'jpg' if fmt in ['jpg', 'jpeg'] else 'png'
        content_type = 'image/jpeg' if out_ext == 'jpg' else 'image/png'

        doc = fitz.open(stream=file_bytes, filetype='pdf')
        total_pages = len(doc)
        if total_pages == 0:
            raise ValueError('O arquivo PDF não contém páginas.')

        if total_pages == 1:
            page = doc[0]
            pix = page.get_pixmap(dpi=dpi)
            img_bytes = pix.tobytes(out_ext)
            return img_bytes, content_type, f'pagina_01.{out_ext}'

        # Múltiplas páginas -> empacotar em ZIP
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            num_digits = max(2, len(str(total_pages)))
            for i in range(total_pages):
                page = doc[i]
                pix = page.get_pixmap(dpi=dpi)
                img_data = pix.tobytes(out_ext)
                img_name = f'pagina_{str(i + 1).zfill(num_digits)}.{out_ext}'
                zip_file.writestr(img_name, img_data)

        zip_buf.seek(0)
        return zip_buf.getvalue(), 'application/zip', 'imagens_pdf.zip'

    @staticmethod
    def images_to_pdf(files):
        """
        Converte uma lista de imagens para um único arquivo PDF.
        :param files: lista de arquivos de imagem (UploadedFile ou bytes)
        :return: bytes do PDF gerado
        """
        if not files:
            raise ValueError('Nenhuma imagem enviada para conversão.')

        pil_images = []
        for f in files:
            raw_bytes = f.read() if hasattr(f, 'read') else f
            img = Image.open(io.BytesIO(raw_bytes))
            # Garantir formato RGB (remover canal alpha para evitar problemas com PDF)
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                bg = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                bg.paste(img, mask=img.split()[-1])
                pil_images.append(bg)
            else:
                pil_images.append(img.convert('RGB'))

        if not pil_images:
            raise ValueError('Nenhuma imagem válida para gerar PDF.')

        output_buf = io.BytesIO()
        first_img = pil_images[0]
        other_images = pil_images[1:] if len(pil_images) > 1 else []

        first_img.save(
            output_buf,
            format='PDF',
            save_all=True,
            append_images=other_images
        )
        output_buf.seek(0)
        return output_buf.getvalue()

