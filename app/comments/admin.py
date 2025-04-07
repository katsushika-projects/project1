from django.contrib import admin

from .models import Comment


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "comment",
        "item_id",
    )


admin.site.register(Comment, CommentAdmin)
