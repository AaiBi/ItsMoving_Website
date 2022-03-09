from django import forms
from base_app.models import Mover, Number_Mover_Quote_Request_PerDay, Quote_Request


class Mover_Form(forms.ModelForm):
    class Meta:
        model = Mover
        fields = [
            'ref', 'company_name', 'company_phone_number', 'Adresse', 'employee_number', 'number_max_quote_request',
            'website', 'TVA_number', 'Postal_Code', 'City', 'company_statut', 'company_description',
            'logo', 'validated', 'activated', 'country', 'moving_type1'
        ]


class Quote_Request_Form(forms.ModelForm):
    class Meta:
        model = Quote_Request
        fields = [
            'ref', 'country', 'City_Departure', 'Adresse_Departure', 'Postal_Code_Departure', 'Residence_Number_or_Name_Departure',
            'Residence_Departure', 'Number_Room_Departure', 'Country_Arrival', 'City_Arrival', 'Adresse_Arrival',
            'Residence_Number_or_Name_Arrival', 'Postal_Code_Arrival', 'Residence_Arrival', 'packing_service',
            'packaging_materials', 'furniture_assembly_disassembly', 'furniture_storage', 'Additional_informations',
            'firstname', 'lastname', 'email', 'email_sent_to_customer', 'phone_number', 'distributed', 'moving_date',
            'moving_date1', 'moving_date2', 'moving_type1', 'moving_type2'
        ]


class Number_Mover_Quote_Request_PerDay_Form(forms.ModelForm):
    class Meta:
        model = Number_Mover_Quote_Request_PerDay
        fields = [
            'number_quote_received_the_same_day'
        ]