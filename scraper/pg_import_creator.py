import os
import logging
from time import strftime, time
import scraper_constants


class PostgressImportCreator():
  def __init__(self, tv_dir, movie_dir, movies_per_file=500, tv_shows_per_file=2000):
    self.tv_dir = tv_dir
    self.movie_dir = movie_dir
    self.movies_per_file = movies_per_file
    self.tv_shows_per_file = tv_shows_per_file
    self.current_movie_file = None
    self.current_tv_file = None
    self.log_file = 'postgressimportcreator_{time}.log'.format(time=strftime('%Y-%m-%d %H-%M'))

    logging.basicConfig(filename=self.log_file, format='%(levelname)s: %(message)s', level=logging.DEBUG)

  def create_import_files(self):
    """Kicks off process to create postgres import files
    """
    start_time = time()

    if os.path.exists(self.movie_dir) and os.path.exists(self.tv_dir):
      self.create_movie_import_files()
      self.create_tv_import_files()
    else:
      raise ValueError('The provided movie and/or tv directory does not exist.')

    total_time = time() - start_time
    logging.info('Total time: ' + str(total_time))
  
  def create_movie_import_files(self):
    """Creates a series of movie data import files for postgres
    """
    logging.info('Starting movie file creation')
    movie_file_count = 0
    movies_per_file_counter = 0

    self.increment_movie_import_file(movie_file_count)

    movie_letters = os.listdir(self.movie_dir)
    for letter in movie_letters:
      try:
        movie_files = os.listdir('/'.join([self.movie_dir, letter]))
        for movie_file in movie_files:
          movie_title, movie_year = self.extract_movie_title_and_year_from_file_name(movie_file)
          with open('/'.join([self.movie_dir, letter, movie_file])) as movie_file_contents:
            movie_script = movie_file_contents.read()
          
          movie_data = '\t'.join([movie_title, movie_year, movie_script]) + '\n'
          self.current_movie_file.write(movie_data)
          movies_per_file_counter += 1

          if movies_per_file_counter >= self.movies_per_file:
            movie_file_count += 1
            self.increment_movie_import_file(movie_file_count)
            movies_per_file_counter = 0
      except Exception as e:
        logging.error('Error occurred while processing ' + movie_file + ': ' + str(e))
  
  def create_tv_import_files(self):
    """Creates a series of TV data import files for postgres
    """
    # for each letter in tv_dir
    #   for each show in letter
    #     store initial year
    #     for each season
    #       calculate season year
    #       for each episode in season
    #         up to tv_shows_per_file
    #           tv title \t show \t season number \t season year \t script

    print('sup')
  
  def extract_movie_title_and_year_from_file_name(self, file_name):
    """Returns the year from a movie file name, e.g. 'Movie Title_1994.txt' -> '1994'
    """
    title = file_name[:]
    if title.lower().endswith('.txt'):
      title = title[:-4]
      last_underscore = title.rfind('_')
      if last_underscore > -1:
        return title[:last_underscore], title[last_underscore+1:]
      else:
        raise ValueError('File name has incorrect date format: ' + file_name)

      return title
    else:
      raise ValueError('File name in unsupported format: ' + file_name)
  
  def increment_movie_import_file(self, counter):
    if self.current_movie_file:
      self.current_movie_file.close()
    self.current_movie_file = open('pg_import_movie_' + str(counter) + '.txt', 'w')
  
  def increment_tv_import_file(self, counter):
    if self.current_tv_file:
      self.current_tv_file.close()
    self.current_tv_file = open('pg_import_tv_' + str(counter) + '.txt')


if __name__ == '__main__':
  pg = PostgressImportCreator('/users/allen/documents/dev/script-database/scraper/test/tv', '/users/allen/documents/dev/script-database/scraper/test/movies')
  pg.create_import_files()