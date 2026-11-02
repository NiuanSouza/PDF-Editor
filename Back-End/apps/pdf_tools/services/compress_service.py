import io
import pikepdf


class CompressService:
    @staticmethod
    def compress(file_bytes, level='recommended'):
        """
        Otimiza e reduz o tamanho do arquivo PDF.
        :param file_bytes: bytes do PDF original
        :param level: 'extreme', 'recommended', 'low'
        :return: bytes do PDF comprimido
        """
        with pikepdf.open(io.BytesIO(file_bytes)) as pdf:
            pdf.remove_unreferenced_resources()

            # Compressão estrutural de streams e objetos
            output_buf = io.BytesIO()
            pdf.save(
                output_buf,
                compress_streams=True,
                object_stream_mode=pikepdf.ObjectStreamMode.generate,
                linearize=True,
            )
            output_buf.seek(0)
            compressed_bytes = output_buf.getvalue()

            # Se por acaso a compressão resultar maior que o original (ex: PDF já hipercomprimido),
            # retornar o menor dos dois.
            if len(compressed_bytes) < len(file_bytes):
                return compressed_bytes
            return file_bytes

