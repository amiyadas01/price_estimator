from django.db import models 
  
class SearchQuery(models.Model): 
    query        = models.CharField(max_length=300) 
    searched_at  = models.DateTimeField(auto_now_add=True) 
    user_email   = models.EmailField(blank=True, null=True) 
    user_session = models.CharField(max_length=100, blank=True) 
    result_count = models.IntegerField(default=0) 
    price_min    = models.CharField(max_length=50, blank=True) 
    price_max    = models.CharField(max_length=50, blank=True) 
 
    class Meta: 
        ordering = ['-searched_at'] 
        verbose_name_plural = 'Search Queries' 
 
    def __str__(self): 
        return f"{self.query} ({self.searched_at.strftime('%d %b %Y')})" 
