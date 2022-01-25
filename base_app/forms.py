from django import forms
from base_app.models import Mover


class Mover_Form(forms.ModelForm):
    class Meta:
        model = Mover
        fields = [
            'ref', 'company_name', 'company_email', 'company_phone_number', 'Adresse', 'employee_number',
            'website', 'TVA_number', 'Postal_Code', 'City', 'company_statut', 'company_description', 'facebook_link',
            'instagram_link', 'twitter_link', 'linkedin_link', 'logo', 'country', 'validated', 'activated'
        ]