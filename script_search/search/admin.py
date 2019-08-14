from django.contrib import admin
from .models import Script, ScriptMigration


# Register custom models to be able to view on admin site
admin.site.register(Script)
admin.site.register(ScriptMigration)
