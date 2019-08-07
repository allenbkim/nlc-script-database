import psycopg2
from os import path, listdir
from os.path import isfile, join


class ScriptImporter:
  def __init__(self, movie_path, tv_path, db_info):
    self.movie_path = movie_path
    self.tv_path = tv_path
    self.db_info = db_info
    self.conn_str = "dbname='{db_name}' user='{db_user}' host='{db_host}' password='{db_password}'".format(
                    db_name=self.db_info['db_name'],
                    db_user=self.db_info['db_user'],
                    db_host=self.db_info['db_host'],
                    db_password=self.db_info['db_password']
                  ) 
    self.conn = None
  
  def import_scripts(self):
    try:
      self.conn = psycopg2.connect(self.conn_str)
      self.conn.autocommit = True
    except:
      raise ValueError('Failed to connect to database with given information.')

    self.import_movies()
    self.import_tv_shows()

    self.conn.close()
  
  def import_movies(self):
    movie_dir_raw = listdir(self.movie_path)
    movies = [movie for movie in movie_dir_raw if path.isfile(path.join(self.movie_path, movie))]

    for movie in movies:
      movie_title = self.replace_tokens(movie)
      movie_year = self.get_year_from_file(movie)
      if (movie_year > -1):
        movie_script = self.get_script_file_contents(path.join(self.movie_path, movie))
        # INSERT command
      else:
        print('Something wrong with movie year')
  
  def import_tv_shows(self):
    tv_show_dir = listdir(self.tv_path)
    tv_shows = [show for show in tv_show_dir if not path.isfile(path.join(self.tv_path, show))]

    for tv_show in tv_shows:
      year = self.get_year_from_file(tv_show)
      seasons_dir = listdir(path.join(self.tv_path, tv_show))
      seasons = [season for season in seasons_dir if not path.isfile(path.join(self.tv_path, tv_show, season))]

      for season in seasons:
        season_num = self.get_season_from_directory(season)
        eps_dir = listdir(path.join(self.tv_path, tv_show, season))
        eps = [ep for ep in eps_dir if path.isfile(path.join(self.tv_path, tv_show, season, ep))]

        for ep in eps:
          ep_num = self.get_episode_from_file(ep)
          ep_script = self.get_script_file_contents(path.join(self.tv_path, tv_show, season, ep))
          # INSERT command to postgres
  
  def get_year_from_file(self, file_name):
    year = -1
    if file_name.find('_') > -1:
      year_str = file_name.split('_')[-1]
      if year_str.find('.') > -1:
        year = int(year_str.split('.')[0])
      else:
        year = int(year_str)
    
    return year
  
  def get_season_from_directory(self, dir_name):
    season = -1
    if dir_name.find(' ') > -1:
      season = int(dir_name.split(' ')[1])

    return season
  
  def get_episode_from_file(self, file_name):
    episode = -1
    if file_name.find('.') > -1:
      episode = int(file_name.split('.')[0])
    
    return episode
  
  def replace_tokens(self, title):
    fixed_title = (title + '.')[:-1]
    fixed_title = fixed_title.replace('__BSLASH__', '\\')
    fixed_title = fixed_title.replace('__SLASH__', '/')
    fixed_title = fixed_title.replace('__COLON__', ':')
    fixed_title = fixed_title.replace('__STAR__', '*')
    fixed_title = fixed_title.replace('__LT__', '<')
    fixed_title = fixed_title.replace('__GT__', '>')
    fixed_title = fixed_title.replace('__Q__', '?')
    fixed_title = fixed_title.replace('__PIPE__', '|')

    return fixed_title
  
  def get_script_file_contents(self, file_name):
    script = None
    with open(file_name, 'r') as handle:
      script = handle.read()
    
    return script
