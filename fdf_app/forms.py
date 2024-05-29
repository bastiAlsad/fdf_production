from django import forms
from .models import Kursprogramm, Uebungen_Models
from django.contrib.auth.models import User

class KursForm(forms.ModelForm):
    class Meta:
        model = Kursprogramm
        fields = ["name", "note"]

    def __init__(self, *args, **kwargs):
        super(KursForm, self).__init__(*args, **kwargs)
        self.fields['note'].required = False
        self.fields['note'].label = 'Neue Vorgefertigten Übungen erstellen'
 # not  fields = ["laxout_user_name, note"] !


class User(forms.ModelForm):
    model = User
    fields = ["username", "password"]

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Uebungen_Models
        fields = ["execution", "name", "dauer", "videoPath", "looping", "timer", "required", "imagePath", "onlineVideoPath", ]

class CustomerForm(forms.Form):
    vorname = forms.CharField(max_length=100, required=True)
    nachname = forms.CharField(max_length=100, required=True)
    straße = forms.CharField(max_length=100, required=True)
    hausnummer = forms.IntegerField(required=True)
    email = forms.EmailField(required=True)
    stadt = forms.CharField(max_length=100, required=True)
    postleitzahl = forms.IntegerField(required=True)
    kurs = forms.CharField(max_length=100, required=True)