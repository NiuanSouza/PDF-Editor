import io
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from reportlab.pdfgen import canvas
from PIL import Image


def create_sample_pdf(num_pages=2, text="PDF Teste"):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    for p in range(1, num_pages + 1):
        c.drawString(100, 750, f"{text} - Página {p}")
        c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def create_sample_image(color=(255, 0, 0), size=(100, 100)):
    buf = io.BytesIO()
    img = Image.new('RGB', size, color=color)
    img.save(buf, format='JPEG')
    buf.seek(0)
    return buf.getvalue()


class ApiEndpointsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_merge_pdfs(self):
        pdf1 = SimpleUploadedFile("doc1.pdf", create_sample_pdf(2, "Doc 1"), content_type="application/pdf")
        pdf2 = SimpleUploadedFile("doc2.pdf", create_sample_pdf(3, "Doc 2"), content_type="application/pdf")
        
        response = self.client.post('/api/merge/', {'files': [pdf1, pdf2]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(len(response.content) > 0)

    def test_split_pdf_all(self):
        pdf = SimpleUploadedFile("doc.pdf", create_sample_pdf(3, "Split All"), content_type="application/pdf")
        response = self.client.post('/api/split/', {'file': pdf, 'mode': 'all'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')

    def test_split_pdf_range(self):
        pdf = SimpleUploadedFile("doc.pdf", create_sample_pdf(5, "Split Range"), content_type="application/pdf")
        response = self.client.post('/api/split/', {'file': pdf, 'mode': 'range', 'page_range': '1-2, 4'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_compress_pdf(self):
        pdf = SimpleUploadedFile("doc.pdf", create_sample_pdf(2, "Compress"), content_type="application/pdf")
        response = self.client.post('/api/compress/', {'file': pdf, 'level': 'recommended'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_rotate_pdf(self):
        pdf = SimpleUploadedFile("doc.pdf", create_sample_pdf(2, "Rotate"), content_type="application/pdf")
        response = self.client.post('/api/rotate/', {'file': pdf, 'angle': '90', 'page_selection': 'all'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_protect_and_unlock_pdf(self):
        pdf = SimpleUploadedFile("doc.pdf", create_sample_pdf(1, "Secret"), content_type="application/pdf")
        
        # Protect
        protect_res = self.client.post('/api/protect/', {'file': pdf, 'password': 'mysecretpassword123'})
        self.assertEqual(protect_res.status_code, 200)
        protected_bytes = protect_res.content

        # Unlock with wrong password
        locked_file = SimpleUploadedFile("locked.pdf", protected_bytes, content_type="application/pdf")
        wrong_res = self.client.post('/api/unlock/', {'file': locked_file, 'password': 'wrong'})
        self.assertEqual(wrong_res.status_code, 401)

        # Unlock with correct password
        locked_file_ok = SimpleUploadedFile("locked.pdf", protected_bytes, content_type="application/pdf")
        unlock_res = self.client.post('/api/unlock/', {'file': locked_file_ok, 'password': 'mysecretpassword123'})
        self.assertEqual(unlock_res.status_code, 200)
        self.assertEqual(unlock_res['Content-Type'], 'application/pdf')

    def test_watermark_pdf(self):
        pdf = SimpleUploadedFile("doc.pdf", create_sample_pdf(2, "Base Doc"), content_type="application/pdf")
        response = self.client.post('/api/watermark/', {'file': pdf, 'text': 'CONFIDENCIAL'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_images_to_pdf(self):
        img1 = SimpleUploadedFile("img1.jpg", create_sample_image((255, 0, 0)), content_type="image/jpeg")
        img2 = SimpleUploadedFile("img2.jpg", create_sample_image((0, 255, 0)), content_type="image/jpeg")
        response = self.client.post('/api/images-to-pdf/', {'files': [img1, img2]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_word_to_pdf_and_pdf_to_word(self):
        import docx
        doc_buf = io.BytesIO()
        d = docx.Document()
        d.add_heading("Título de Teste Word", level=1)
        d.add_paragraph("Este é um teste de conversão bidirecional de Word para PDF.")
        d.save(doc_buf)
        doc_buf.seek(0)

        # 1. Word -> PDF
        word_file = SimpleUploadedFile("teste.docx", doc_buf.getvalue(), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        w2p_res = self.client.post('/api/word-to-pdf/', {'file': word_file})
        self.assertEqual(w2p_res.status_code, 200)
        self.assertEqual(w2p_res['Content-Type'], 'application/pdf')
        pdf_bytes = w2p_res.content
        self.assertTrue(len(pdf_bytes) > 0)

        # 2. PDF -> Word
        pdf_file = SimpleUploadedFile("convertido.pdf", pdf_bytes, content_type="application/pdf")
        p2w_res = self.client.post('/api/pdf-to-word/', {'file': pdf_file})
        self.assertEqual(p2w_res.status_code, 200)
        self.assertEqual(p2w_res['Content-Type'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        self.assertTrue(len(p2w_res.content) > 0)

