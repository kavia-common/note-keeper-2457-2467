from django.db import models

# PUBLIC_INTERFACE
class Note(models.Model):
    """A model representing a Note entity in the Note-Keeper application."""
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
