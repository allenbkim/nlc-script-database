-- Creates full-text search index and trigger to update a tf_vector column

CREATE INDEX idx_fts_script_vec ON usc_script USING gin(script_vector)

CREATE FUNCTION update_script_vec() RETURNS trigger
	LANGUAGE 'plpgsql' VOLATILE NOT LEAKPROOF
AS $BODY$
BEGIN
	NEW.script_vector :=
		setweight(to_tsvector('pg_catalog.english',
			coalesce(NEW.title,'')), 'A') ||
		setweight(to_tsvector('pg_catalog.english',
			coalesce(NEW.script,'')), 'D');
	RETURN NEW;
END
$BODY$;

CREATE TRIGGER update_script_vec
	BEFORE INSERT OR UPDATE ON usc_script
	FOR EACH ROW EXECUTE PROCEDURE update_script_vec()