from django.contrib import admin
from .models import Documento, Processo, Anexo

admin.site.register(Documento)
admin.site.register(Processo)
admin.site.register(Anexo)
