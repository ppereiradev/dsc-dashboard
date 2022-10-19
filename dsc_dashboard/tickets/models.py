from django.db import models

class Ticket(models.Model):
    
    id_ticket = models.CharField(max_length=50)
    number = models.CharField(max_length=50)
    title = models.CharField(max_length=1000)
    created_at = models.DateTimeField()
    close_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    create_article_type = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    group = models.CharField(max_length=50)

    def __str__(self):
        return f"Number: { self.number } - Title: {self.title} - State: { self.state } - Group: { self.group }"
