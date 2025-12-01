from django import forms

class PageSpeedForm(forms.Form):
    url = forms.URLField(
        label="آدرس سایت",
        widget=forms.URLInput(attrs={
            "class": "form-control",
            "placeholder": "https://example.com",
        })
    )
    strategy = forms.ChoiceField(
        label="نوع تست",
        choices=(
            ("mobile", "موبایل"),
            ("desktop", "دسکتاپ"),
        ),
        widget=forms.Select(attrs={"class": "form-select"})
    )
