from django import forms
from base_app.models import Mover, Number_Mover_Quote_Request_PerDay


class Mover_Form(forms.ModelForm):
    class Meta:
        model = Mover
        fields = [
            'ref', 'company_name', 'company_phone_number', 'Adresse', 'employee_number', 'number_max_quote_request',
            'website', 'TVA_number', 'Postal_Code', 'City', 'company_statut', 'company_description',
            'logo', 'validated', 'activated', 'country', 'moving_type1'
        ]


class Number_Mover_Quote_Request_PerDay_Form(forms.ModelForm):
    class Meta:
        model = Number_Mover_Quote_Request_PerDay
        fields = [
            'number_quote_received_the_same_day'
        ]