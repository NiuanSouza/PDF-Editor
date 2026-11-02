import io
import pikepdf


class SecurityService:
    @staticmethod
    def protect(file_bytes, user_password, owner_password=None):
        """
        Aplica proteção por senha e criptografia AES-256 no PDF.
        :param file_bytes: bytes do PDF original
        :param user_password: senha de abertura do documento
        :param owner_password: senha de permissões do proprietário (opcional)
        :return: bytes do PDF protegido
        """
        if not user_password:
            raise ValueError('Informe uma senha para proteger o documento.')

        with pikepdf.open(io.BytesIO(file_bytes)) as pdf:
            encryption = pikepdf.Encryption(
                owner=owner_password or user_password,
                user=user_password,
                R=6,  # AES-256
            )
            output_buf = io.BytesIO()
            pdf.save(output_buf, encryption=encryption)
            output_buf.seek(0)
            return output_buf.getvalue()

    @staticmethod
    def unlock(file_bytes, password=''):
        """
        Remove a criptografia e proteção por senha de um PDF.
        :param file_bytes: bytes do PDF protegido
        :param password: senha atual do PDF
        :return: bytes do PDF desbloqueado
        """
        try:
            pdf = pikepdf.open(io.BytesIO(file_bytes), password=password)
        except pikepdf.PasswordError:
            raise ValueError('Senha incorreta para desbloquear o arquivo PDF.')
        except Exception as e:
            raise ValueError(f'Não foi possível abrir o PDF: {str(e)}')

        with pdf:
            output_buf = io.BytesIO()
            pdf.save(output_buf)  # Salva sem encriptação
            output_buf.seek(0)
            return output_buf.getvalue()

