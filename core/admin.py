from django.contrib import admin
from .models import SearchQuery

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ('query', 'searched_at', 'user_email', 'result_count', 'price_min', 'price_max')
    search_fields = ('query', 'user_email')
    list_filter = ('searched_at',)
