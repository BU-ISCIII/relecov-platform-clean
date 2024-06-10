from django.contrib import admin
import relecov_dashboard.models


class GraphicJsonFileAdmin(admin.ModelAdmin):
    list_display = ["graphic_name"]


admin.site.register(relecov_dashboard.models.GraphicJsonFile, GraphicJsonFileAdmin)
