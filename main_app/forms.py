from dataclasses import field
from django.forms import ModelForm
from .models import Feeding

class FeedingForm(ModelForm):
    class Meta:    # This was running behind the scenes to create ModelForm
        model = Feeding
        fields = ['date', 'meal']
