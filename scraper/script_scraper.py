from bs4 import BeautifulSoup
import os
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import strftime, time
import re
import logging


class ScriptScraper:
  def __init__(self, tv_scripts, letters, site_url, thread_count, download_directory):
    self.tv_scripts = tv_scripts
    self.letters = letters
    self.site_url = site_url
    self.scripts_url = ''
    self.thread_count = thread_count
    self.download_directory = download_directory
    self.log_file = 'scriptscraper_{time}.log'.format(time=strftime('%Y-%m-%d %H-%M'))

    logging.basicConfig(filename=self.log_file, format='%(levelname)s: %(message)s', level=logging.DEBUG)
  
  def scrape_site(self):
    logging.info('Starting scraping process:\n\tTV:{tv}\n\tLetters:{letters}'
                  .format(
                    tv=str(self.tv_scripts),
                    letters=str(self.letters)
                  )
                )
    start_time = time()

    if self.tv_scripts:
      self.scripts_url = self.site_url + '/tv_show_episode_scripts.php'
    else:
      self.scripts_url = self.site_url + '/movie_scripts.php'

    self.ensure_script_file_path(self.download_directory.split('/'))
    
    with ThreadPoolExecutor(self.thread_count) as executor:
      letter_results = {executor.submit(self.iterate_title_letter, letter): letter for letter in self.letters}
    for letter_result in as_completed(letter_results):
      try:
        letter = letter_results[letter_result]
        script_count, show_count, missing_dates = letter_result.result()
        if self.tv_scripts:
          logging.info('Shows for {letter} - {count}'.format(letter=letter, count=show_count))
        logging.info('Scripts for {letter} - {count}'.format(letter=letter, count=script_count))
        logging.info('Missing for {letter} - {missing}'.format(letter=letter, missing=missing_dates))
      except Exception as e:
        logging.error('Error occurred for ' + letter + ': ' + str(e))
    
    total_time = time() - start_time
    logging.info('Total time: ' + str(total_time))
  
  def iterate_title_letter(self, letter):
    # Soupify the script page for each letter
    letter_page = urlopen(self.scripts_url + '?order=' + letter)
    letter_page_soup = BeautifulSoup(letter_page, 'lxml')

    # Find the number of pages for each letter
    letter_page_links = letter_page_soup.select('div.pagination a')
    if len(letter_page_links) > 0:
      letter_pages = int(letter_page_links[-1].get_text())
    else:
      letter_pages = 1

    script_count, show_count, missing_dates = self.iterate_letter_pages(letter, letter_pages, letter_page_soup)  
    return script_count, show_count, missing_dates
  
  def iterate_letter_pages(self, letter, num_pages, letter_page_soup):
    missing_dates = []
    current_page = 1
    show_count = 0
    script_count = 0

    while current_page <= num_pages:
      if current_page > 1:
        letter_page = urlopen(self.scripts_url + '?order=' + letter + '&page=' + str(current_page))
        letter_page_soup = BeautifulSoup(letter_page, 'lxml')
      
      title_links = letter_page_soup.select('a.script-list-item')
      for title_link in title_links:
        title_page = title_link['href']
        title = title_link.get_text()
        title_date = '<<DATE>>'
        dates = re.findall(r'[(][\d]{4,4}[)]', title)
        if len(dates) > 0:
          # If a date in the format (####) exists then take the last one and remove from the title
          title_date = dates[-1][1:-1]
          title = title[:-7]
        else:
          # Make note of the title without a date on "Springfield, Springfield"
          missing_dates.append(title)
        
        if self.tv_scripts:
          added_scripts = self.scrape_tv_scripts(title, title_date, title_page)
          script_count += added_scripts
        else:
          self.scrape_movie_scripts(title, title_date, title_page)
          script_count += 1
        
        show_count += 1
        
      current_page += 1
    
    return script_count, show_count, missing_dates
  
  def scrape_tv_scripts(self, tv_show_title, tv_show_date, tv_episodes_page_url):
    script_count = 0
    tv_episodes_page = urlopen(self.site_url + tv_episodes_page_url)
    tv_episodes_page_soup = BeautifulSoup(tv_episodes_page, 'lxml')

    season_divs = tv_episodes_page_soup.select('div.season-episodes')
    for season_div in season_divs:
      episode_links = season_div.select('a.season-episode-title')
      for episode_link in episode_links:
        episode_script_page_url = episode_link['href']
        episode_script_page = urlopen(self.site_url + '/' + episode_script_page_url)
        episode_script_page_soup = BeautifulSoup(episode_script_page, 'lxml')

        raw_script = episode_script_page_soup.find('div', class_='scrolling-script-container').get_text()
        clean_script = self.clean_script(raw_script)

        clean_title = self.clean_title(tv_show_title)
        path_elements = self.download_directory.split('/') + \
                        [clean_title + '_' + tv_show_date, season_div.find('h3').get_text()]
        self.ensure_script_file_path(path_elements)
        ep_path = '/'.join(path_elements)
        ep_filename = self.clean_title(episode_link.get_text()) + '.txt'

        self.save_script_file('/'.join([ep_path, ep_filename]), clean_script)
        script_count += 1
    
    return script_count
  
  def scrape_movie_scripts(self, movie_title, movie_date, movie_script_page_url):
    movie_script_page = urlopen(self.site_url + movie_script_page_url)
    movie_script_soup = BeautifulSoup(movie_script_page, 'lxml')

    raw_script = movie_script_soup.find('div', class_='scrolling-script-container').get_text()
    clean_script = self.clean_script(raw_script)

    movie_filename = self.clean_title(movie_title) + '_' + str(movie_date) + '.txt'
    self.save_script_file('/'.join([self.download_directory, movie_filename]), clean_script)
  
  def clean_title(self, raw_title):
    clean_title = (raw_title + '.')[:-1]
    clean_title = clean_title.strip()
    clean_title = clean_title.replace('/', '<<SLASH>>')
    clean_title = clean_title.replace(':', '<<COLON>>')
    return clean_title
  
  def clean_script(self, raw_script):
    clean_script = re.sub(r'\s+', ' ', raw_script).strip()
    clean_script = clean_script.replace('\\', '')
    return clean_script
  
  def ensure_script_file_path(self, path_elements):
    if path_elements is not None and len(path_elements) > 0:
      current_path = ''
      for path_element in path_elements:
        if current_path == '':
          current_path = path_element
        else:
          current_path = '/'.join([current_path, path_element])
        if not os.path.exists(current_path):
          os.mkdir(current_path)
  
  def save_script_file(self, file_name, script):
    with open(file_name, 'w+') as handle:
      handle.write(script)
      handle.close()
