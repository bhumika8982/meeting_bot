from django.db import models

class Meeting(models.Model):

    meeting_link = models.URLField()
    transcript = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)