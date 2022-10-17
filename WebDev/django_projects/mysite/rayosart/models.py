from django.db import models

# Create your models here.

class Account(models.Model):
    """Model representing a user account."""
    
    user_id = None

    def __str__(self):
        return self.user_id
    
class Commision(models.Model):
    """Model representing a user commission."""
    
    user_id = None
    commisioned = None
    closed = None

    def __str__(self):
        return self.user_id
class Product(models.Model):
    """Model representing a product."""
    
    product_id = None
    title = None
    series = None
    size = None
    tags = None

    def __str__(self):
        return self.product_id