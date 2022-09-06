from django.forms import ModelForm
from .models import Profile

class SettingForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_img', 'bio', 'location']
