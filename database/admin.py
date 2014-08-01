from django.contrib import admin
from database.models import Project, Sample

# Register your models here.
class ProjectAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,              {'fields': ['project_name']}),
        ('Start Date',      {'fields': ['start_date'], 'classes': ['collapse']})
    ]
    inlines=[ChoiceInline]

admin.site.register(ProjectAdmin)