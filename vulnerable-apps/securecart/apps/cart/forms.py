from django import forms


class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        max_value=99,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '99'
        })
    )
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
