from django import forms

class ContinentForm(forms.Form):
    CONTINENT_CHOICES = [
        ('Africa', 'Africa'),
        ('Americas', 'Americas'),
        ('Asia', 'Asia'),
        ('Europe', 'Europe'),
        ('Oceania', 'Oceania'),
        ('Antarctic', 'Antarctic'),
    ]
    continent = forms.ChoiceField(choices=CONTINENT_CHOICES, label='Select Continent') 