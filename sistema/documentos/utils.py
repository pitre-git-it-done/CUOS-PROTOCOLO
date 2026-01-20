import os
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def protocolo_curto(protocolo):
    return str(protocolo).replace('-', '')[:7]

def gerar_protocolo_pdf(documento):
    pasta = os.path.join(settings.MEDIA_ROOT, 'protocolos')
    os.makedirs(pasta, exist_ok=True)

    nome_arquivo = f'protocolo_{documento.protocolo}.pdf'
    caminho_pdf = os.path.join(pasta, nome_arquivo)

    c = canvas.Canvas(caminho_pdf, pagesize=A4)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "COMPROVANTE DE RECEBIMENTO DE DOCUMENTOS")

    c.setFont("Helvetica", 11)
    c.drawString(50, 760, f"Protocolo: {protocolo_curto(documento.protocolo)}")
    c.drawString(50, 740, f"Nome: {documento.nome_requerente}")
    c.drawString(50, 720, f"CPF: {documento.cpf}")
    c.drawString(50, 700, f"Tipo de Documento: {documento.tipo_documento}")
    c.drawString(50, 680, f"Data de Envio: {documento.data_envio.strftime('%d/%m/%Y %H:%M')}")

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 640, "Este documento comprova o recebimento eletrônico.")

    c.showPage()
    c.save()

    return nome_arquivo, caminho_pdf


def gerar_protocolo_pdf_processo(processo):
    pasta = os.path.join(settings.MEDIA_ROOT, 'protocolos')
    os.makedirs(pasta, exist_ok=True)

    nome_arquivo = f'protocolo_{processo.protocolo}.pdf'
    caminho_pdf = os.path.join(pasta, nome_arquivo)

    c = canvas.Canvas(caminho_pdf, pagesize=A4)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "COMPROVANTE DE ENVIO DE PROCESSO")

    c.setFont("Helvetica", 11)
    c.drawString(50, 760, f"Protocolo: {protocolo_curto(processo.protocolo)}")
    c.drawString(50, 740, f"Usuario: {processo.usuario}")
    c.drawString(50, 720, f"Nome do Requerente: {processo.nome_requerente}")
    c.drawString(50, 700, f"Tipo de Processo: {processo.tipo_processo}")
    c.drawString(50, 680, f"Descricao: {processo.descricao or '-'}")
    c.drawString(50, 660, f"Data de Envio: {processo.data_envio.strftime('%d/%m/%Y %H:%M')}")

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 640, "Este documento comprova o envio do processo.")

    c.showPage()
    c.save()

    return nome_arquivo, caminho_pdf
