from django import forms
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from base_app.models import Mover_Country, Mover_Region, Mover_Moving_Type2, Mover_Quote_Request, Quote_Request_Rejected


class EditUserForm(UserChangeForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'username'
        ]


class EditUserPasswordForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = [
            'old_password', 'new_password1', 'new_password2'
        ]
        widgets = {
            'old_password': forms.PasswordInput(attrs={'class': 'form-control', 'name': 'old_password', 'type': 'password',
                                               'placeholder': 'Entrez votre actuel mot de passe :'}),
            'new_password1': forms.PasswordInput(attrs={'class': 'form-control', 'name': 'new_password1', 'type': 'password',
                                                   'placeholder': 'Entrez votre nouveau mot de passe :'}),
            'new_password2': forms.PasswordInput(attrs={'class': 'form-control', 'name': 'new_password2', 'type': 'password',
                                                   'placeholder': 'Entrez a nouveau votre nouveau mot de passe :'}),
        }

    def clean(self):
        cleaned_data = super(EditUserPasswordForm, self).clean()
        password = cleaned_data.get('password')


class EditMoverCountryForm(forms.ModelForm):
    class Meta:
        model = Mover_Country
        fields = [
            'country_name', 'departure', 'arrival'
        ]


class EditMoverRegionForm(forms.ModelForm):
    class Meta:
        model = Mover_Region
        fields = [
            'region_name'
        ]


class EditMoverMovingType2Form(forms.ModelForm):
    class Meta:
        model = Mover_Moving_Type2
        fields = [
            'moving_type2_name'
        ]


class MoverQuoteRequestForm(forms.ModelForm):
    class Meta:
        model = Mover_Quote_Request
        fields = [
            'treated', 'rejected'
        ]