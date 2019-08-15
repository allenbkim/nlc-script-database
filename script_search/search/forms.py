from django import forms


class SearchForm(forms.Form):
  search_terms = forms.CharField(min_length=1, max_length=200, strip=True, required=True)
  year_filter_low = forms.IntegerField(min_value=1900, max_value=2030, required=False)
  year_filter_high = forms.IntegerField(min_value=1900, max_value=2030, required=False)
