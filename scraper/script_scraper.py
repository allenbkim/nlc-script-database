from bs4 import BeautifulSoup
import os
from urllib.request import urlopen
import re

class ScriptScraper:
  def __init__(self, tv_scripts, letters, site_url, download_directory):
    self.tv_scripts = tv_scripts
    self.letters = letters
    self.site_url = site_url
    self.scripts_url = ''
    self.download_directory = download_directory
    self.missing_dates = []
  
  def scrape_site(self):
    if self.tv_scripts:
      self.scripts_url = self.site_url + '/tv_show_episode_scripts.php'
    else:
      self.scripts_url = self.site_url + '/movie_scripts.php'

    if not os.path.exists(self.download_directory):
      os.mkdir(self.download_directory)
    
    for letter in self.letters:
      self.iterate_title_letters(letter)
  
  def iterate_title_letters(self, letter):
    # Soupify the script page for each letter
    letter_page = urlopen(self.scripts_url + '?order=' + letter)
    letter_page_soup = BeautifulSoup(letter_page, 'html.parser')

    # Find the number of pages for each letter
    letter_pages = int(letter_page_soup.select('div.pagination a')[-1].get_text())

    current_page = 1
    while current_page <= letter_pages:
      if current_page > 1:
        letter_page = urlopen(self.scripts_url + '?order=' + letter + '&page=' + str(current_page))
        letter_page_soup = BeautifulSoup(letter_page, 'html.parser')
      
      title_links = letter_page_soup.select('a.script-list-item')
      for title_link in title_links:
        title_page = title_link['href']
        title = title_link.get_text()
        title_date = '==MISSING_DATE=='
        dates = re.findall(r'[(][\d]{4,4}[)]', title)
        if len(dates) > 0:
          # If a date in the format (####) exists then take the last one and remove from the title
          title_date = dates[-1]
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
    tv_episodes_page_soup = BeautifulSoup(tv_episodes_page, 'html.parser')

    season_divs = tv_episodes_page_soup.select('div.season-episodes')
    for season_div in season_divs:
      episode_links = season_div.select('a.season-episode-title')
      for episode_link in episode_links:
        episode_script_page_url = episode_link['href']
        episode_script_page = urlopen(self.site_url + '/' + episode_script_page_url)
        episode_script_page_soup = BeautifulSoup(episode_script_page, 'html.parser')

        raw_script = episode_script_page_soup.find('div', class_='scrolling-script-container').get_text()
        clean_script = self.clean_script(raw_script)

        # TODO: validate file path and name
        ep_path = '/'.join([tv_show_title + '_' + tv_show_date, season_div.find('h3').get_text()])
        if not os.path.exists(self.download_directory + '/' + tv_show_title + '_' + tv_show_date):
          os.mkdir(self.download_directory + '/' + tv_show_title + '_' + tv_show_date)
        if not os.path.exists(self.download_directory + '/' + tv_show_title + '_' + tv_show_date + '/' + season_div.find('h3').get_text()):
          os.mkdir(self.download_directory + '/' + tv_show_title + '_' + tv_show_date + '/' + season_div.find('h3').get_text())
        ep_filename = episode_link.get_text()+ '.txt'
        with open(self.download_directory + '/' + ep_path + '/' + ep_filename, 'w+') as handle:
          handle.write(clean_script)
          handle.close()
  
  def scrape_movie_scripts(self, movie_title, movie_date, movie_script_page_url):
    movie_script_page = urlopen(self.site_url + movie_script_page_url)
    movie_script_soup = BeautifulSoup(movie_script_page, 'html.parser')

    raw_script = movie_script_soup.find('div', class_='scrolling-script-container').get_text()
    clean_script = self.clean_script(raw_script)

    # TODO: validate file path and name
    movie_filename = movie_title + '_' + str(movie_date) + '.txt'
    with open(self.download_directory + '/' + movie_filename, 'w+') as handle:
      handle.write(clean_script)
      handle.close()
  
  def clean_script(self, raw_script):
    # TODO: define and implement cleaning procedure
    clean_script = (raw_script + '.')[:-1]
    clean_script = clean_script.strip()
    return clean_script
