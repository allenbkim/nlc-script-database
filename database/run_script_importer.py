from script_importer import ScriptImporter


def run_script_importer(movie_path, tv_path, db_info):
  script_importer = ScriptImporter(movie_path, tv_path, db_info)
  print('Starting script import process')
  script_importer.import_scripts()
  print('Finished script import process')


if __name__ == '__main__':
  # Parameters for importing scripts into the postgres database
  movie_path = ''
  tv_path = ''
  db_info = {}

  # Engage!
  run_script_importer(movie_path, tv_path, db_info)
