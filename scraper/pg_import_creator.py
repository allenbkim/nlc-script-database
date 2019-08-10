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
    self.log_file = 'postgressimportcreator_{time}.log'.format(time=strftime('%Y-%m-%d %H-%M'))

    logging.basicConfig(filename=self.log_file, format='%(levelname)s: %(message)s', level=logging.DEBUG)

  def create_import_files(self):
    start_time = time()

    # for each movie in movie_dir
    #   up to movie_per_file
    #     movie title \t year \t script

    # for each letter in tv_dir
    #   for each show in letter
    #     store initial year
    #     for each season
    #       calculate season year
    #       for each episode in season
    #         up to tv_shows_per_file
    #           tv title \t show \t season number \t season year \t script

    total_time = time() - start_time
    logging.info('Total time: ' + str(total_time))
