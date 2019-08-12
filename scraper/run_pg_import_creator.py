import pg_import_creator


def main():
  tv_dir = ''
  movie_dir = ''
  print('Starting import file creation')
  import_creator = pg_import_creator.PostgressImportCreator(tv_dir, movie_dir)
  import_creator.create_import_files()
  print('Import file creation finished. Please check log files.')


if __name__ == '__main__':
  main()
