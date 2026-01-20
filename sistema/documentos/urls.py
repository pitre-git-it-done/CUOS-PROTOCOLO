from django.urls import path
from .views import formulario_publico, consulta_protocolo, sucesso
from .views import LoginInternoView, LogoutInternoView, painel_interno
from .views import relatorio_excel, anexos_zip, atualizar_processo
from .views_conta import cadastrar, LoginUsuarioView, LogoutUsuarioView, conta, esqueci_senha
from .views import area_usuario
from .views import novo_processo



urlpatterns = [
    path('', formulario_publico, name='formulario'),
    path('consulta/', consulta_protocolo, name='consulta_protocolo'),
    path('sucesso/<uuid:protocolo>/', sucesso, name='sucesso'),

    path('interno/login/', LoginInternoView.as_view(), name='login_interno'),
    path('interno/logout/', LogoutInternoView.as_view(), name='logout_interno'),
    path('interno/', painel_interno, name='painel_interno'),
    path('interno/relatorio.xlsx', relatorio_excel, name='relatorio_excel'),
    path('interno/processos/<int:processo_id>/anexos.zip', anexos_zip, name='anexos_zip'),
    path('interno/processos/<int:processo_id>/atualizar/', atualizar_processo, name='atualizar_processo'),
    path('conta/cadastrar/', cadastrar, name='cadastrar'),
    path('conta/login/', LoginUsuarioView.as_view(), name='login_usuario'),
    path('conta/logout/', LogoutUsuarioView.as_view(), name='logout_usuario'),
    path('conta/ajustes/', conta, name='conta'),
    path('conta/esqueci/', esqueci_senha, name='esqueci_senha'),
    path('area/', area_usuario, name='area_usuario'),
    path('processo/novo/', novo_processo, name='novo_processo'),



]
