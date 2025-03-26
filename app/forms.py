from django import forms
from app.constants import SEX, SCIENTIFIC_AREA, POSITION, COMMUNICATION_CHANNELS
from api.models import City, ComplaintType, RoadType

SEX_EMPTY = [('','Indique su sexo')] + list(SEX)
SCI_AREA_EMPTY = [('','Seleccione un área')] + list(SCIENTIFIC_AREA)
POSITION_EMPTY = [('','Seleccione su nivel académico')] + list(POSITION)
CHANNEL_EMPTY = [('','Indique un canal de comunicación')] + list(COMMUNICATION_CHANNELS)
BECAL = [(False, 'Indique si es becario de BECAL'), (False, 'No'), (True, 'Si')]


class UserRegistrationForm(forms.Form):
    username = forms.CharField(label='Nombre de usuario *', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su nombre de usuario',
        }
    ))

    password = forms.CharField(label='Contraseña *', widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña',
        }
    ))

class RegistrationForm(forms.Form):
    complaint_type = forms.ModelChoiceField(queryset=ComplaintType.objects.all(), label="Tipo de denuncia *", empty_label="Tipo de denuncia", widget=forms.Select(attrs={
        'class': 'form-control',
    }))
    city = forms.ModelChoiceField(queryset=City.objects.all(), label="Ciudad *", empty_label="Ciudad", widget=forms.Select(attrs={
        'class': 'form-control',
    }))
    road_type = forms.ModelChoiceField(queryset=RoadType.objects.all(), label="Tipo de calle", empty_label="Tipo de calle", widget=forms.Select(attrs={
        'class': 'form-control',
    }))
    description = forms.CharField(label="Descripción", widget=forms.Textarea(attrs={
        'class': 'form-control',
    }))
    photo = forms.FileField(label="Foto", widget=forms.FileInput(attrs={
        'class': 'form-control',
    }))
    location_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    location_lat = forms.CharField(widget=forms.HiddenInput(), required=True)
    location_lng = forms.CharField(widget=forms.HiddenInput(), required=True)


class RegistrationEditForm(forms.Form):
    location_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    location_lat = forms.CharField(widget=forms.HiddenInput(), required=False)
    location_lng = forms.CharField(widget=forms.HiddenInput(), required=False)