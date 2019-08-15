from django.shortcuts import render
from .models import Script
from time import time


def index(request):
  return render(request, 'search/index.html')

def search(request):
  search_context = None
  if request.method == 'POST':
    start_time = time()

    # User performed a search
    search_params = {}
    search_params['search_term'] = request.POST['search_term'].strip()
    search_params['year_filter_low'] = request.POST['year_filter_low'].strip() or 1900
    search_params['year_filter_high'] = request.POST['year_filter_high'].strip() or 2100
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

    if results:
      search_context = {}
      search_context['search_results'] = []
      search_context['script_hits'] = len(results)
      search_context['snippet_hits'] = 0

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
        search_context['snippet_hits'] += len(snippets)
        search_context['search_results'].append(search_result)
      
      elapsed = time() - start_time
      search_context['elapsed'] = '%.4f' % elapsed

  return render(request, 'search/searchscripts.html', context=search_context)

def view_script(request):
  return render(request, 'search/viewscript.html')
