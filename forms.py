from django import forms
from models import *
from django.forms import ModelForm, ModelChoiceField


class RUTFReporterForm(forms.ModelForm):
##    class Meta:
##        model = RUTFReporter
##        location = ModelChoiceField(HealthPost.objects.filter(code = 'ESS'))
        
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    grandfather_name = forms.CharField(max_length=30)
    location = forms.ModelChoiceField(queryset = HealthPost.objects.filter(code = 'ESS'))


class HealthPostForm(forms.ModelForm):
    parent = forms.ModelChoiceField(queryset = HealthPost.objects.filter(code = 'DAW'))
