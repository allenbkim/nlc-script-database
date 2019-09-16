from django.db import migrations


class Migration(migrations.Migration):
  dependencies = [
    # Requires initial 'search' app migration to create tables
    ('search', '0001_initial'),
  ]

  migration = '''
    CREATE FUNCTION update_search_content_func() RETURNS trigger
      LANGUAGE 'plpgsql' VOLATILE NOT LEAKPROOF
    AS $BODY$
    BEGIN
      NEW.search_content :=
        setweight(to_tsvector('pg_catalog.english',
          coalesce(NEW.title,'')), 'A') ||
        setweight(to_tsvector('pg_catalog.english',
          coalesce(NEW.script_content,'')), 'D');
      RETURN NEW;
    END
    $BODY$;

    CREATE TRIGGER update_search_content_trig
      BEFORE INSERT OR UPDATE ON search_script
      FOR EACH ROW EXECUTE PROCEDURE update_search_content_func()
  '''
  reverse_migration = '''
    DROP TRIGGER update_search_content_trig ON search_script;
    DROP FUNCTION update_search_content_func();
  '''
  operations = [
    migrations.RunSQL(migration, reverse_migration)
  ]
