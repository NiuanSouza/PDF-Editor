import io
import pikepdf


class MergeService:
    @staticmethod
    def merge(files):
        """
        Mescla múltiplos arquivos PDF em um único documento.
        :param files: lista de arquivos (UploadedFile ou file-like objects com .read())
        :return: bytes do PDF mesclado
        """
        if len(files) < 2:
            raise ValueError('Envie pelo menos 2 arquivos PDF para mesclar.')

        merged = pikepdf.Pdf.new()

        for f in files:
            file_bytes = f.read() if hasattr(f, 'read') else f
            src = pikepdf.Pdf.open(io.BytesIO(file_bytes))
            merged.pages.extend(src.pages)

        output_buffer = io.BytesIO()
        merged.save(output_buffer)
        output_buffer.seek(0)
        return output_buffer.getvalue()

