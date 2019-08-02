from bs4 import BeautifulSoup
import os
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
from time import time
import re

class ScriptScraper:
  def __init__(self, tv_scripts, letters, site_url, thread_count, download_directory):
    self.tv_scripts = tv_scripts
    self.letters = letters
    self.site_url = site_url
    self.scripts_url = ''
    self.thread_count = thread_count
    self.download_directory = download_directory
    self.missing_dates = []
  
  def scrape_site(self):
    start_time = time()

    if self.tv_scripts:
      self.scripts_url = self.site_url + '/tv_show_episode_scripts.php'
    else:
      self.scripts_url = self.site_url + '/movie_scripts.php'

    if not os.path.exists(self.download_directory):
      os.mkdir(self.download_directory)
    
    with ThreadPoolExecutor(self.thread_count) as executor:
      results = executor.map(self.iterate_title_letters, self.letters)
    
    total_time = time() - start_time
    print('Total time:', str(total_time))
  
  def iterate_title_letters(self, letter):
    # Soupify the script page for each letter
    letter_page = urlopen(self.scripts_url + '?order=' + letter)
    letter_page_soup = BeautifulSoup(letter_page, 'lxml')

    # Find the number of pages for each letter
    letter_page_links = letter_page_soup.select('div.pagination a')
    if len(letter_page_links) > 0:
      letter_pages = int(letter_page_links[-1].get_text())
    else:
      letter_pages = 1

    current_page = 1
    while current_page <= letter_pages:
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
          self.missing_dates.append(title)
        
        if self.tv_scripts:
          self.scrape_tv_scripts(title, title_date, title_page)
        else:
          self.scrape_movie_scripts(title, title_date, title_page)

      current_page += 1
  
  def scrape_tv_scripts(self, tv_show_title, tv_show_date, tv_episodes_page_url):
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

        # TODO: Clean up logic to ensure file path
        clean_title = self.clean_title(tv_show_title)
        ep_path = '/'.join([clean_title + '_' + tv_show_date, season_div.find('h3').get_text()])
        if not os.path.exists(self.download_directory + '/' + clean_title + '_' + tv_show_date):
          os.mkdir(self.download_directory + '/' + clean_title + '_' + tv_show_date)
        if not os.path.exists(self.download_directory + '/' + clean_title + '_' + tv_show_date + '/' + season_div.find('h3').get_text()):
          os.mkdir(self.download_directory + '/' + clean_title + '_' + tv_show_date + '/' + season_div.find('h3').get_text())
        ep_filename = self.clean_title(episode_link.get_text()) + '.txt'

        self.save_script_file(ep_path + '/' + ep_filename, clean_script)
  
  def scrape_movie_scripts(self, movie_title, movie_date, movie_script_page_url):
    movie_script_page = urlopen(self.site_url + movie_script_page_url)
    movie_script_soup = BeautifulSoup(movie_script_page, 'lxml')

    raw_script = movie_script_soup.find('div', class_='scrolling-script-container').get_text()
    clean_script = self.clean_script(raw_script)

    movie_filename = self.clean_title(movie_title) + '_' + str(movie_date) + '.txt'
    self.save_script_file(movie_filename, clean_script)
  
  def clean_title(self, raw_title):
    clean_title = (raw_title + '.')[:-1]
    clean_title = clean_title.strip()
    clean_title = clean_title.replace('/', '<<FS>>')
    return clean_title
  
  def clean_script(self, raw_script):
    # TODO: define and implement cleaning procedure
    clean_script = (raw_script + '.')[:-1]
    clean_script = clean_script.strip()
    return clean_script
  
  def save_script_file(self, file_name, script):
    with open('/'.join([self.download_directory, file_name]), 'w+') as handle:
      handle.write(script)
      handle.close()
