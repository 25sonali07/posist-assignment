from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Base_model(models.Model):
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now_add=True)

    class Meta:
        abstract = True


class Channel(Base_model):
    name = models.TextField(max_length=256)
    description = models.TextField(max_length=8000)
    users = models.TextField(max_length=10000)
    tags = models.TextField(max_length=10000)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL,related_name="Channel",null=True,)

    def __str__(self):
        return self.name
    

class ChannelPost(Base_model):
    post_data = models.TextField(max_length=5000)
    user = models.ForeignKey(User, on_delete=models.SET_NULL,related_name="ChannelPost",null=True,)
    channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True,)

    def __str__(self):
        return self.post_data
    
