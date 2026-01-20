import secrets
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import render, redirect


User = get_user_model()


class CadastroUsuarioForm(UserCreationForm):
    first_name = forms.CharField(label='Nome Completo', max_length=150)
    email = forms.EmailField(label='Email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = 'Nome Completo'
        self.fields['username'].label = 'Nome de usuario'
        self.fields['email'].label = 'Email'
        self.fields['password1'].label = 'Senha'
        self.fields['password2'].label = 'Confirmacao de senha'
        self.fields['username'].help_text = ''
        self.fields['email'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.order_fields(['first_name', 'email', 'username', 'password1', 'password2'])

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Email ja cadastrado.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

def cadastrar(request):
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('area_usuario')
    else:
        form = CadastroUsuarioForm()

    return render(request, 'documentos/cadastrar.html', {'form': form})


class ContaForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = 'Nome Completo'
        self.fields['email'].label = 'Email'

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Email ja cadastrado.')
        return email


class SenhaForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Senha atual'
        self.fields['new_password1'].label = 'Nova senha'
        self.fields['new_password2'].label = 'Confirmacao da nova senha'
        self.fields['old_password'].help_text = ''
        self.fields['new_password1'].help_text = ''
        self.fields['new_password2'].help_text = ''


def conta(request):
    if not request.user.is_authenticated:
        return redirect('login_usuario')

    if request.method == 'POST':
        if request.POST.get('acao') == 'dados':
            form_conta = ContaForm(request.POST, instance=request.user)
            form_senha = SenhaForm(request.user)
            if form_conta.is_valid():
                form_conta.save()
                messages.success(request, 'Dados atualizados com sucesso.')
                return redirect('conta')
        else:
            form_conta = ContaForm(instance=request.user)
            form_senha = SenhaForm(request.user, request.POST)
            if form_senha.is_valid():
                user = form_senha.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Senha atualizada com sucesso.')
                return redirect('conta')
    else:
        form_conta = ContaForm(instance=request.user)
        form_senha = SenhaForm(request.user)

    return render(request, 'documentos/conta.html', {
        'form_conta': form_conta,
        'form_senha': form_senha,
    })


def esqueci_senha(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        user = User.objects.filter(email__iexact=email).first()
        if user:
            temp_password = secrets.token_urlsafe(8)
            user.set_password(temp_password)
            user.save()
            send_mail(
                'Senha temporaria',
                (
                    'Geramos uma senha temporaria para sua conta.\n\n'
                    f'Senha: {temp_password}\n\n'
                    'Acesse o sistema e altere sua senha em Conta.'
                ),
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        messages.success(request, 'Se o email existir, enviamos uma senha temporaria.')
        return redirect('esqueci_senha')

    return render(request, 'documentos/esqueci_senha.html')


class LoginUsuarioView(LoginView):
    template_name = 'documentos/login_usuario.html'

    def get_success_url(self):
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to
        if self.request.user.is_staff:
            return '/interno/'
        return '/area/'


class LogoutUsuarioView(LogoutView):
    next_page = '/conta/login/'

