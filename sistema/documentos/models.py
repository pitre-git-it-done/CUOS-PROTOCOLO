import uuid
from django.db import models
from django.conf import settings

# ===== LEGADO (mantém o sistema atual funcionando) =====
class Documento(models.Model):
    protocolo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome_requerente = models.CharField(max_length=150)
    cpf = models.CharField(max_length=20)
    tipo_documento = models.CharField(max_length=100)

    arquivo = models.FileField(upload_to='documentos/')
    pdf_protocolo = models.FileField(upload_to='protocolos/', null=True, blank=True)

    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.nome_requerente} - {self.protocolo}'


# ===== NOVO FLUXO (login -> processos -> anexos) =====
class Processo(models.Model):
    STATUS_RECEBIDO = 'recebido'
    STATUS_ANALISE = 'em_analise'
    STATUS_REPROVADO = 'reprovado'
    STATUS_APROVADO = 'aprovado'
    STATUS_CHOICES = [
        (STATUS_RECEBIDO, 'Recebido'),
        (STATUS_ANALISE, 'Em analise'),
        (STATUS_REPROVADO, 'Reprovado'),
        (STATUS_APROVADO, 'Aprovado'),
    ]

    protocolo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='processos')
    nome_requerente = models.CharField(max_length=150, default='')

    tipo_processo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)

    pdf_protocolo = models.FileField(upload_to='protocolos/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_RECEBIDO)
    observacoes = models.TextField(blank=True)
    documento_final = models.FileField(upload_to='documentos_final/', null=True, blank=True)
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario} - {self.protocolo}'


class Anexo(models.Model):
    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField(upload_to='documentos/')
    nome_original = models.CharField(max_length=255, blank=True)
    enviado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Anexo {self.id} - {self.processo.protocolo}'
