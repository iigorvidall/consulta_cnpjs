from django import forms

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
