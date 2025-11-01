from django import forms

class UploadDataForm(forms.Form):
    empresa_nombre = forms.CharField(
        label="Nombre de la Empresa", 
        max_length=100, 
        initial="CrediQ"
    )
    archivo_balance = forms.FileField(
        label="Archivo de Balance General (CSV)",
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )
    archivo_resultados = forms.FileField(
        label="Archivo de Estado de Resultados (CSV)",
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )