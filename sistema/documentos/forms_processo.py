from django import forms
from .models import Processo


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if isinstance(data, (list, tuple)):
            return [super().clean(d, initial) for d in data]
        return super().clean(data, initial)


class ProcessoForm(forms.ModelForm):
    class Meta:
        model = Processo
        fields = ["nome_requerente", "tipo_processo", "descricao"]


class ProcessoAtualizacaoForm(forms.ModelForm):
    class Meta:
        model = Processo
        fields = ["status", "observacoes", "documento_final"]


class AnexosForm(forms.Form):
    anexos = MultipleFileField(
        required=False,
        label="Anexos (selecione 1 ou mais arquivos)",
    )
