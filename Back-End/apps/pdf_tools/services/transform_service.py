import io
import pikepdf
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color


class TransformService:
    @staticmethod
    def rotate(file_bytes, angle=90, page_selection='all'):
        """
        Rotaciona páginas de um arquivo PDF.
        :param file_bytes: bytes do PDF original
        :param angle: 90, 180 ou 270 graus no sentido horário
        :param page_selection: 'all', 'odd' (ímpares), 'even' (pares)
        :return: bytes do PDF rotacionado
        """
        angle = int(angle)
        if angle not in [90, 180, 270]:
            raise ValueError('Ângulo de rotação deve ser 90, 180 ou 270 graus.')

        with pikepdf.open(io.BytesIO(file_bytes)) as pdf:
            for idx, page in enumerate(pdf.pages, start=1):
                should_rotate = False
                if page_selection == 'all':
                    should_rotate = True
                elif page_selection == 'odd' and idx % 2 != 0:
                    should_rotate = True
                elif page_selection == 'even' and idx % 2 == 0:
                    should_rotate = True

                if should_rotate:
                    current_rot = int(page.get('/Rotate', 0))
                    page.Rotate = (current_rot + angle) % 360

            output_buf = io.BytesIO()
            pdf.save(output_buf)
            output_buf.seek(0)
            return output_buf.getvalue()

    @classmethod
    def _create_watermark_page(cls, text, width, height, opacity=0.3, rotation=45, font_size=42):
        """
        Gera um PDF em memória contendo o carimbo de marca d'água nas dimensões exatas da página.
        """
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(width, height))
        can.saveState()

        # Configurar cor e transparência
        can.setFillColor(Color(0.5, 0.5, 0.5, alpha=float(opacity)))
        can.setFont('Helvetica-Bold', font_size)

        # Mover para o centro e rotacionar
        can.translate(width / 2.0, height / 2.0)
        can.rotate(rotation)
        can.drawCentredString(0, 0, text)

        can.restoreState()
        can.save()
        packet.seek(0)
        return packet

    @classmethod
    def watermark(cls, file_bytes, text, opacity=0.3, rotation=45, font_size=42):
        """
        Aplica marca d'água textual em todas as páginas do PDF.
        :param file_bytes: bytes do PDF original
        :param text: texto do carimbo
        :param opacity: opacidade de 0.1 a 1.0
        :param rotation: ângulo do texto (ex: 45)
        :param font_size: tamanho da fonte
        :return: bytes do PDF com marca d'água
        """
        if not text:
            raise ValueError('Informe o texto para a marca d\'água.')

        with pikepdf.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                box = page.mediabox
                width = float(box[2] - box[0])
                height = float(box[3] - box[1])

                wm_pdf_bytes = cls._create_watermark_page(
                    text=text,
                    width=width,
                    height=height,
                    opacity=opacity,
                    rotation=rotation,
                    font_size=font_size
                )

                with pikepdf.open(wm_pdf_bytes) as wm_pdf:
                    wm_page = wm_pdf.pages[0]
                    page.add_overlay(wm_page, pikepdf.Rectangle(box[0], box[1], box[2], box[3]))

            output_buf = io.BytesIO()
            pdf.save(output_buf)
            output_buf.seek(0)
            return output_buf.getvalue()

