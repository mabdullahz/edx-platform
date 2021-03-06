from django.contrib import admin
from .models import Badge, UserBadge

admin.site.register(Badge)


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        # disable add functionality
        return False

    def has_delete_permission(self, request, obj=None):
        # disable delete functionality
        return False

    def get_readonly_fields(self, request, obj=None):
        # make all fields readonly
        return [f.name for f in self.model._meta.fields]
