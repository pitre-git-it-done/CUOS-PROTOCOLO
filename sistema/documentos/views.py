import os
from io import BytesIO
import zipfile

from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from openpyxl import Workbook

from .forms import DocumentoForm
from .forms_processo import AnexosForm, ProcessoAtualizacaoForm, ProcessoForm
from .models import Anexo, Documento, Processo
from .utils import gerar_protocolo_pdf, gerar_protocolo_pdf_processo, protocolo_curto
from .utils_email import notificar_setor


def formulario_publico(request):
    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save()

            nome_arquivo, caminho_pdf = gerar_protocolo_pdf(documento)
            with open(caminho_pdf, 'rb') as f:
                documento.pdf_protocolo.save(nome_arquivo, File(f), save=True)

            notificar_setor(documento)
            return redirect('sucesso', protocolo=documento.protocolo)
    else:
        form = DocumentoForm()

    return render(request, 'documentos/formulario.html', {'form': form})


def sucesso(request, protocolo):
    doc = get_object_or_404(Documento, protocolo=protocolo)
    return render(request, 'documentos/sucesso.html', {'doc': doc})


def consulta_protocolo(request):
    resultado = None
    erro = None

    if request.method == 'POST':
        protocolo = request.POST.get('protocolo', '').strip()
        protocolo_curto_busca = protocolo.replace('-', '').lower()

        try:
            if len(protocolo_curto_busca) == 7:
                qs = Documento.objects.filter(protocolo__startswith=protocolo_curto_busca)
                candidatos = list(qs[:2])
                if len(candidatos) == 1:
                    resultado = candidatos[0]
                elif len(candidatos) > 1:
                    erro = 'Mais de um protocolo encontrado. Use o protocolo completo.'
                else:
                    erro = 'Protocolo nao encontrado.'
            else:
                resultado = Documento.objects.get(protocolo=protocolo)
        except (Documento.DoesNotExist, ValidationError, ValueError):
            erro = 'Protocolo nao encontrado.'

    return render(request, 'documentos/consulta.html', {
        'resultado': resultado,
        'erro': erro
    })


class StaffAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_staff:
            raise forms.ValidationError(
                'Acesso restrito a equipe interna.',
                code='no_staff',
            )


class LoginInternoView(LoginView):
    template_name = 'documentos/login.html'
    authentication_form = StaffAuthenticationForm

    def get_success_url(self):
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to
        return '/interno/'


class LogoutInternoView(LogoutView):
    next_page = '/interno/login/'


@user_passes_test(lambda u: u.is_staff, login_url='/interno/login/')
def painel_interno(request):
    processos = (
        Processo.objects.select_related('usuario')
        .prefetch_related('anexos')
        .order_by('-data_envio')
    )
    termo = request.GET.get('q', '').strip()
    if termo:
        processos = processos.filter(
            models.Q(protocolo__icontains=termo) |
            models.Q(usuario__username__icontains=termo) |
            models.Q(nome_requerente__icontains=termo) |
            models.Q(tipo_processo__icontains=termo) |
            models.Q(descricao__icontains=termo)
        )
    return render(request, 'documentos/painel.html', {
        'processos': processos,
        'status_choices': Processo.STATUS_CHOICES,
        'termo': termo,
    })


@user_passes_test(lambda u: u.is_staff, login_url='/interno/login/')
def relatorio_excel(request):
    data_ini = request.GET.get('data_ini')
    data_fim = request.GET.get('data_fim')

    qs = (
        Processo.objects.select_related('usuario')
        .prefetch_related('anexos')
        .order_by('-data_envio')
    )

    if data_ini:
        di = parse_date(data_ini)
        if di:
            qs = qs.filter(data_envio__date__gte=di)

    if data_fim:
        df = parse_date(data_fim)
        if df:
            qs = qs.filter(data_envio__date__lte=df)

    wb = Workbook()
    ws = wb.active
    ws.title = 'Processos'

    ws.append([
        'Data',
        'Protocolo',
        'Usuario',
        'Requerente',
        'Tipo',
        'Descricao',
        'Status',
        'Observacoes',
        'Documento_Final',
        'PDF_Protocolo',
        'Anexos',
    ])

    for p in qs:
        anexos_urls = []
        for a in p.anexos.all():
            if not a.arquivo:
                continue
            try:
                anexos_urls.append(a.arquivo.url)
            except ValueError:
                continue

        ws.append([
            p.data_envio.strftime('%d/%m/%Y %H:%M'),
            protocolo_curto(p.protocolo),
            str(p.usuario),
            p.nome_requerente,
            p.tipo_processo,
            p.descricao,
            p.get_status_display(),
            p.observacoes,
            p.documento_final.url if p.documento_final else '',
            p.pdf_protocolo.url if p.pdf_protocolo else '',
            ' | '.join(anexos_urls),
        ])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="relatorio_processos.xlsx"'
    return response


@user_passes_test(lambda u: u.is_staff, login_url='/interno/login/')
def anexos_zip(request, processo_id):
    processo = get_object_or_404(
        Processo.objects.prefetch_related('anexos'),
        pk=processo_id,
    )

    anexos = list(processo.anexos.all())
    if not anexos:
        raise Http404("Processo sem anexos.")

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for anexo in anexos:
            if not anexo.arquivo:
                continue
            try:
                with anexo.arquivo.open('rb') as f:
                    nome = os.path.basename(anexo.arquivo.name)
                    zf.writestr(nome, f.read())
            except (FileNotFoundError, ValueError, OSError):
                continue

    buffer.seek(0)
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/zip',
    )
    response['Content-Disposition'] = (
        f'attachment; filename="anexos_processo_{protocolo_curto(processo.protocolo)}.zip"'
    )
    return response


@user_passes_test(lambda u: u.is_staff, login_url='/interno/login/')
def atualizar_processo(request, processo_id):
    processo = get_object_or_404(Processo, pk=processo_id)
    if request.method != 'POST':
        return redirect('painel_interno')

    form = ProcessoAtualizacaoForm(request.POST, request.FILES, instance=processo)
    if form.is_valid():
        form.save()
    return redirect('painel_interno')


@login_required
def area_usuario(request):
    processos = Processo.objects.filter(usuario=request.user).order_by('-data_envio')
    return render(request, 'documentos/area_usuario.html', {'processos': processos})


@login_required
def novo_processo(request):
    if request.method == 'POST':
        form_processo = ProcessoForm(request.POST)
        form_anexos = AnexosForm(request.POST, request.FILES)

        if form_processo.is_valid() and form_anexos.is_valid():
            processo = form_processo.save(commit=False)
            processo.usuario = request.user
            processo.save()

            nome_arquivo, caminho_pdf = gerar_protocolo_pdf_processo(processo)
            with open(caminho_pdf, 'rb') as f:
                processo.pdf_protocolo.save(nome_arquivo, File(f), save=True)

            arquivos = request.FILES.getlist("anexos")
            for f in arquivos:
                Anexo.objects.create(
                    processo=processo,
                    arquivo=f,
                    nome_original=f.name,
                )

            return redirect('area_usuario')
    else:
        form_processo = ProcessoForm()
        form_anexos = AnexosForm()

    return render(
        request,
        'documentos/novo_processo.html',
        {'form_processo': form_processo, 'form_anexos': form_anexos}
    )
