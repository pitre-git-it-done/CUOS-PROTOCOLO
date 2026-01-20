from django.core.mail import send_mail
from django.conf import settings
from .utils import protocolo_curto

def notificar_setor(documento):
    assunto = f'Novo protocolo recebido: {protocolo_curto(documento.protocolo)}'
    mensagem = (
        f'Novo documento recebido.\n\n'
        f'Protocolo: {protocolo_curto(documento.protocolo)}\n'
        f'Nome: {documento.nome_requerente}\n'
        f'CPF: {documento.cpf}\n'
        f'Tipo: {documento.tipo_documento}\n'
    )

    destinatarios = ['gfontessantana@gmail.com']  # troque pelo e-mail real do setor

    send_mail(
        subject=assunto,
        message=mensagem,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=destinatarios,
        fail_silently=False,
    )
