from django.shortcuts import render
from .models import Script


def index(request):
  return render(request, 'search/index.html')

def search(request):
  search_context = None
  if request.method == 'POST':
    # User performed a search
    search_term = request.POST['search_term']
    results = Script.objects.raw('''SELECT
                                      id,
                                      title,
                                      year,
                                      script_type,
                                      ts_rank("search_content", to_tsquery('donation')) as "rank",
                                      ts_headline(script_content,
                                              to_tsquery('donation'),
                                              'StartSel=<b>,StopSel=</b>,MaxFragments=10,' ||
                                              'FragmentDelimiter=;#,MaxWords=10,MinWords=1') as "headline"
                                    FROM
                                      search_script
                                    WHERE
                                      search_content @@ to_tsquery('donation')
                                      AND year > 2010
                                    ORDER BY rank DESC
                                    LIMIT 1000
    ''')

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
        search_result['year'] = result.year
        search_result['rank'] = result.rank
        snippets = result.headline.split(';#')
        search_result['headline'] = snippets
        search_context['snippet_hits'] += len(snippets)
        search_context['search_results'].append(search_result)

  return render(request, 'search/searchscripts.html', context=search_context)

def view_script(request):
  return render(request, 'search/viewscript.html')
