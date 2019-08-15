from django.shortcuts import render
from .models import Script
from .forms import SearchForm
from time import time


def index(request):
  return render(request, 'search/index.html')

def search(request):
  search_context = {}
  if request.method == 'POST':
    start_time = time()
    form = SearchForm(request.POST)
    if form.is_valid():
      # User performed a search
      search_params = {}
      search_params['search_term'] = form.cleaned_data['search_terms']
      search_params['year_filter_low'] = form.cleaned_data['year_filter_low'] or 1900
      search_params['year_filter_high'] = form.cleaned_data['year_filter_high'] or 2100

      print(search_params)
      results = Script.objects.raw("""SELECT
                                        id,
                                        title,
                                        year,
                                        script_type,
                                        season,
                                        episode,
                                        ts_rank("search_content", to_tsquery(%(search_term)s)) as "rank",
                                        ts_headline(script_content,
                                                to_tsquery(%(search_term)s),
                                                'StartSel=<b>,StopSel=</b>,MaxFragments=10,' ||
                                                'FragmentDelimiter=;#,MaxWords=10,MinWords=1') as "headline"
                                      FROM
                                        search_script
                                      WHERE
                                        search_content @@ to_tsquery(%(search_term)s)
                                        AND year >= %(year_filter_low)s
                                        AND year <= %(year_filter_high)s
                                      ORDER BY rank DESC
                                      LIMIT 1000
      """, search_params)

      search_results = create_search_context_from_results(results) 
      search_context['results'] = search_results

      elapsed = time() - start_time
      search_context['elapsed'] = '%.4f' % elapsed
  else:
    form = SearchForm()

  search_context['form'] = form
  return render(request, 'search/searchscripts.html', context=search_context)

def view_script(request):
  return render(request, 'search/viewscript.html')

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
