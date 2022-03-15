from django import forms
from user.models import Quote_Request_Payment


class Mover_Quote_Request_Paiement_Proof_Form(forms.ModelForm):
    class Meta:
        model = Quote_Request_Payment
        fields = [
            'validated'
        ]
