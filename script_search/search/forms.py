from django import forms


class SearchForm(forms.Form):
  year_choices = [('', '')]
  year_choices += [(x, x) for x in range(1920, 2021)]

  script_type_choices = [('All', 'All'), ('T', 'TV'), ('M', 'Movie')]

  search_terms = forms.CharField(min_length=1, max_length=200, strip=True, required=True, widget=forms.Textarea)
  year_filter_low = forms.ChoiceField(choices=year_choices, required=False)
  year_filter_high = forms.ChoiceField(choices=year_choices, required=False)
  script_type = forms.ChoiceField(choices=script_type_choices, widget=forms.RadioSelect, required=True)
