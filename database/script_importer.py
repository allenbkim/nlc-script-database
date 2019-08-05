#import psycopg2
from os import path, listdir
from os.path import isfile, join


class ScriptImporter:
  def __init__(self, movie_path, tv_path, db_info):
    self.movie_path = movie_path
    self.tv_path = tv_path
    self.db_info = db_info
  
  def import_scripts(self):
    # Handle movies
    # Handle tv shows
    print('yo')
  
  def import_movies(self):
    movie_dir_raw = listdir(self.movie_path)
    movies = [movie for movie in movie_dir_raw if path.isfile(movie)]

    for movie in movies:
      # Parse file name to get title and year
      # Open file to get script contents
      # INSERT command to postgres
      print('yo')
  
  def import_tv_shows(self):
    tv_show_dir = listdir(self.tv_path)
    tv_shows = [show for show in tv_show_dir if not path.isfile(show)]

    for tv_show in tv_shows:
      # Parse file name to get title and year
      seasons_dir = listdir(self.tv_path + '/' + tv_show)
      seasons = [season for season in seasons_dir if not path.isfile(season)]

      for season in seasons:
        # Parse the file name to get season number
        eps_dir = listdir(self.tv_path + '/' + tv_show + '/' + season)
        eps = [ep for ep in eps_dir if path.isfile(path.join(self.tv_path + '/' + tv_show + '/' + season, ep))]

        for ep in eps:
          # Parse the file name to get episode number
          # Open file to get script contents
          # INSERT command to postgres
          print('yo')
