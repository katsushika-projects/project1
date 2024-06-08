from django.contrib import admin

from .models import Campus, University


class CampusAdmin(admin.ModelAdmin):
    list_display = (
        "campus",
        "university",
    )
    ordering = (
        "university",
        "campus",
    )


class UniversityAdmin(admin.ModelAdmin):
    ordering = ("name",)


admin.site.register(University, UniversityAdmin)
admin.site.register(Campus, CampusAdmin)
