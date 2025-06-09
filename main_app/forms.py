from django import forms
from .models import SurveyResponse

class SurveyResponseForm(forms.ModelForm):
    class Meta:
        model = SurveyResponse
        fields = '__all__'
