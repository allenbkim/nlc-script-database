from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic
from .models import Script
from .forms import SearchForm
from time import time
import csv


def index(request):
  """Home page of the USC Norman Lear Center. No login required.
  """
  return render(request, 'search/index.html')

@login_required
def search(request):
  """Script search page. Login and search.can_search permission required.
  """
  search_context = {}
  if request.method == 'POST':
    start_time = time()
    form = SearchForm(request.POST)
    if form.is_valid():
      if 'search' in form.data:
        # User performed a search
        search_params = {}
        search_params['search_terms'] = form.cleaned_data['search_terms']
        search_params['year_filter_low'] = form.cleaned_data['year_filter_low'] or 1900
        search_params['year_filter_high'] = form.cleaned_data['year_filter_high'] or 2100
        search_params['script_type'] = form.cleaned_data['script_type']

        query = create_search_query(search_params)
        results = Script.objects.raw(query, search_params)

        search_results = create_search_context_from_results(results) 
        search_context['results'] = search_results

        elapsed = time() - start_time
        search_context['elapsed'] = '%.4f' % elapsed

        # Cache the last results for export
        if 'search_results' in search_results:
          request.session['last_results'] = search_results['search_results']
        else:
          request.session['last_results'] = None
      elif 'export' in form.data:
        checked_ids = request.POST.getlist('chk_result')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=scripts.csv'
        selected_rows = [row for row in request.session['last_results'] if str(row['id']) in checked_ids]
        writer = csv.writer(response)
        writer.writerow(['Script Type', 'Title', 'Year', 'Season', 'Episode', 'Mentions'])
        for selected_row in selected_rows:
          writer.writerow(['TV' if selected_row['script_type'] == 'T' else 'Movie',
                           selected_row['title'],
                           selected_row['year'],
                           selected_row['season'] if selected_row['script_type'] == 'T' else '',
                           selected_row['episode'] if selected_row['script_type'] == 'T' else '',
                           clean_mentions_for_export(selected_row['headline'])
          ])
        
        return response
  else:
    form = SearchForm(initial={'script_type': 'T'})

  search_context['form'] = form
  return render(request, 'search/searchscripts.html', context=search_context)

class ScriptDetailView(LoginRequiredMixin, generic.DetailView):
  model = Script
  template_name = 'search/viewscript.html'

def logout_search(request):
  logout(request)
  return render(request, 'registration/logout.html')

def search_query_help(request):
  return render(request, 'search/queryhelp.html')

def create_search_query(search_params):
  query_template = """SELECT
                        id,
                        title,
                        year,
                        script_type,
                        season,
                        episode,
                        ts_rank("search_content", to_tsquery('english', %(search_terms)s)) as "rank",
                        ts_headline('english', script_content,
                                to_tsquery('english', %(search_terms)s),
                                'StartSel=<b>,StopSel=</b>,MaxFragments=10,' ||
                                'FragmentDelimiter=;#,MaxWords=10,MinWords=5') as "headline"
                      FROM
                        search_script
                      WHERE
                        search_content @@ to_tsquery('english', %(search_terms)s)
                        AND year >= %(year_filter_low)s
                        AND year <= %(year_filter_high)s
                        {script_type_filter}
                      ORDER BY rank DESC
                      LIMIT 500
  """

  if search_params['script_type'] == 'T' or search_params['script_type'] == 'M':
    script_type_filter = 'AND script_type=\'{script_type}\''.format(script_type=search_params['script_type'])
  else:
    script_type_filter = ''
  
  return query_template.format(script_type_filter=script_type_filter)

def create_search_context_from_results(results):
  """Converts SQL query results to dictionary for HTML template.
  """
  search_results = {}
  if results:
    search_results['search_results'] = []
    search_results['script_hits'] = len(results)
    search_results['snippet_hits'] = 0

    for result in results:
      search_result = {}
      search_result['id'] = result.id
      search_result['title'] = result.title
      search_result['script_type'] = result.script_type
      search_result['season'] = result.season
      search_result['episode'] = result.episode
      search_result['year'] = result.year
      search_result['rank'] = result.rank
      snippets = result.headline.split(';#')
      search_result['headline'] = snippets
      search_results['snippet_hits'] += len(snippets)
      search_results['search_results'].append(search_result)
  
  return search_results

def clean_mentions_for_export(mentions):
  cleaned_mentions = ''

  for mention in mentions:
    cleaned_mentions += mention.replace('<b>', '').replace('</b>', '')
    cleaned_mentions += ';#'

  return cleaned_mentions
