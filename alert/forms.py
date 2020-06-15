from django import forms

class UnknownForm(forms.Form):
    chk_info = forms.MultipleChoiceField(
        #chk_info = LIST_OF_VALID_chk_info, # this is optional
        widget  = forms.CheckboxSelectMultiple,
    )