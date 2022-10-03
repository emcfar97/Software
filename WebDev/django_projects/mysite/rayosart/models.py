from django.db import models

# Create your models here.

class Commisions(models.Model):
    
    user_id = None
    commisioned = None
    closed = None

    def __str__(self):
        return self.question_text