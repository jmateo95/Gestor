from django import forms
from django.core.exceptions import ValidationError
from .models import Variables

class TimeInputWithTimeType(forms.TimeInput):
    input_type = 'time'

class VariablesForm(forms.ModelForm):
    class Meta:
        model = Variables
        fields = ['hora_inicio', 'hora_fin', 'duracion']
        widgets = {
            'hora_inicio': TimeInputWithTimeType(attrs={'class': 'timeinput form-control'}),
            'hora_fin': TimeInputWithTimeType(attrs={'class': 'timeinput form-control'}),
        }
        labels = {
            'duracion': 'Duracion en minutos',
        }
