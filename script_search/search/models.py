from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex, BTreeIndex


class ScriptMigration(models.Model):
  title = models.TextField()
  script_type = models.CharField(max_length=1)
  year_text = models.TextField()
  season_text = models.TextField(null=True)
  episode_text = models.TextField(null=True)
  episode_title = models.TextField(null=True)
  script_content = models.TextField()


class Script(models.Model):
  title = models.TextField()
  script_type = models.CharField(max_length=1)
  year = models.IntegerField()
  season = models.IntegerField(null=True)
  episode = models.IntegerField(null=True)
  episode_title = models.TextField(null=True)
  script_content = models.TextField()
  search_content = SearchVectorField(null=True)

  class Meta:
      indexes = [BTreeIndex(fields=["year"]), BTreeIndex(fields=["script_type"]), GinIndex(fields=["search_content"])]
