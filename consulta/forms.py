from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

class ConsultaForm(forms.Form):
    cnpjs = forms.CharField(required=False, label='CNPJ(s)', widget=forms.TextInput(attrs={'placeholder': 'Digite um ou mais CNPJs, separados por vírgula'}))
    csv_file = forms.FileField(required=False, label='Ou envie um arquivo CSV/XLSX:')

    def clean(self):
        cleaned_data = super().clean()
        cnpjs = cleaned_data.get('cnpjs', '').strip()
        csv_file = cleaned_data.get('csv_file')
        if not cnpjs and not csv_file:
            raise forms.ValidationError('Preencha o campo de CNPJ(s) ou envie um arquivo CSV.')
        if cnpjs and not all(c.isdigit() or c in ',. -/\n\t' for c in cnpjs):
            raise forms.ValidationError('O campo CNPJ(s) só pode conter números, vírgulas, traços, barras e espaços.')
        if csv_file and not (csv_file.name.lower().endswith('.csv') or csv_file.name.lower().endswith('.xlsx')):
            raise forms.ValidationError('O arquivo enviado deve ser um CSV ou XLSX.')
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(label='Usuário ou E-mail')
    password = forms.CharField(widget=forms.PasswordInput, label='Senha')


class SignupForm(forms.ModelForm):
    # Campos pedidos: usuário (login), email, senha, repetir senha
    password1 = forms.CharField(widget=forms.PasswordInput, label='Senha')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Repita a senha')

    class Meta:
        model = get_user_model()
        fields = ['username', 'email']
        labels = {
            'username': 'Usuário',
            'email': 'E-mail',
        }

    def clean_username(self):
        username = (self.cleaned_data.get('username') or '').strip()
        if not username:
            raise forms.ValidationError('Informe o usuário.')
        User = get_user_model()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Usuário já cadastrado.')
        return username

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if not email:
            raise forms.ValidationError('Informe o e-mail.')
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('E-mail já cadastrado.')
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('As senhas não conferem.')
        if p1:
            validate_password(p1)
        return cleaned

    def save(self, commit=True):
        User = get_user_model()
        user = User(username=self.cleaned_data['username'], email=self.cleaned_data['email'])
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
