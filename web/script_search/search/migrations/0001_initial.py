# Generated by Django 2.2.4 on 2019-08-13 22:48

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('script_type', models.CharField(max_length=1)),
                ('year', models.IntegerField()),
                ('season', models.IntegerField(null=True)),
                ('episode', models.TextField(null=True)),
                ('episode_title', models.TextField(null=True)),
                ('script_content', models.TextField()),
                ('search_content', django.contrib.postgres.search.SearchVectorField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ScriptMigration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('script_type', models.CharField(max_length=1)),
                ('year_text', models.TextField()),
                ('season_text', models.TextField(null=True)),
                ('episode_text', models.TextField(null=True)),
                ('episode_title', models.TextField(null=True)),
                ('script_content', models.TextField()),
            ],
        ),
        migrations.AddIndex(
            model_name='script',
            index=django.contrib.postgres.indexes.BTreeIndex(fields=['year'], name='search_scri_year_ed51c3_btree'),
        ),
        migrations.AddIndex(
            model_name='script',
            index=django.contrib.postgres.indexes.BTreeIndex(fields=['script_type'], name='search_scri_script__c45587_btree'),
        ),
        migrations.AddIndex(
            model_name='script',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_content'], name='search_scri_search__07b131_gin'),
        ),
    ]