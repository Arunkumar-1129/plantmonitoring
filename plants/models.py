from django.db import models

# We'll use PyMongo directly for MongoDB operations
# These models are just for Django admin if needed

class Disease(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
