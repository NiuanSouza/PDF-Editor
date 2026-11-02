import os
import io
import shutil
import subprocess
import tempfile
import uuid


class WordConversionService:
    @staticmethod
    def docx_to_pdf(file_bytes, original_filename='document.docx'):
        """
        Converte arquivo Word (.docx, .doc, .rtf, .odt) para PDF usando LibreOffice Headless.
        :param file_bytes: bytes do documento de entrada
        :param original_filename: nome original para manter a extensão (.docx/.doc)
        :return: bytes do PDF gerado
        """
        ext = os.path.splitext(original_filename)[1].lower()
        if ext not in ['.docx', '.doc', '.rtf', '.odt', '.txt']:
            ext = '.docx'

        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = os.path.join(tmp_dir, f'input{ext}')
            with open(input_path, 'wb') as f:
                f.write(file_bytes)

            profile_dir = os.path.join(tmp_dir, f'lo_prof_{uuid.uuid4().hex}')
            os.makedirs(profile_dir, exist_ok=True)

            cmd = [
                'soffice',
                '--headless',
                f'-env:UserInstallation=file://{profile_dir}',
                '--convert-to', 'pdf',
                '--outdir', tmp_dir,
                input_path,
            ]

            try:
                proc = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=60,
                    check=False
                )
            except FileNotFoundError:
                raise RuntimeError('LibreOffice (soffice) não está instalado no servidor para conversão DOCX -> PDF.')
            except subprocess.TimeoutExpired:
                raise TimeoutError('A conversão do arquivo Word excedeu o tempo limite de 60 segundos.')

            output_pdf_path = os.path.join(tmp_dir, 'input.pdf')
            if not os.path.exists(output_pdf_path):
                stderr_msg = proc.stderr.decode('utf-8', errors='ignore')
                raise RuntimeError(f'Falha ao converter Word para PDF: {stderr_msg}')

            with open(output_pdf_path, 'rb') as f:
                return f.read()

    @staticmethod
    def pdf_to_docx(file_bytes):
        """
        Converte PDF para documento Word (.docx) editável usando pdf2docx.
        :param file_bytes: bytes do PDF
        :return: bytes do arquivo DOCX gerado
        """
        try:
            from pdf2docx import Converter
        except ImportError:
            raise RuntimeError('Biblioteca pdf2docx não está instalada no servidor.')

        with tempfile.TemporaryDirectory() as tmp_dir:
            input_pdf_path = os.path.join(tmp_dir, 'input.pdf')
            output_docx_path = os.path.join(tmp_dir, 'output.docx')

            with open(input_pdf_path, 'wb') as f:
                f.write(file_bytes)

            try:
                cv = Converter(input_pdf_path)
                cv.convert(output_docx_path)
                cv.close()
            except Exception as e:
                raise RuntimeError(f'Erro na extração do documento Word: {str(e)}')

            if not os.path.exists(output_docx_path):
                raise RuntimeError('Não foi possível gerar o arquivo Word.')

            with open(output_docx_path, 'rb') as f:
                return f.read()

