from django.contrib import admin

from .models import Image, Item, Like, Report


class ImageInline(admin.TabularInline):
    model = Image


class ItemAdmin(admin.ModelAdmin):
    inlines = [ImageInline]
    list_display = (
        "name",
        "seller",
    )
    list_filter = ("listing_status",)
    search_fields = ("name",)
    ordering = ("-updated_at",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )


admin.site.register(Item, ItemAdmin)
admin.site.register(Like)
admin.site.register(Report)
