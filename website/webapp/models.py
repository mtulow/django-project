from django.db import models

# Create your models here.


class Tweet(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=300)
    # edit_history_ids = models
    created_at = models.DateTimeField()
    language = models.CharField(max_length=2)
    author_id = models.ForeignKey('User', on_delete=models.CASCADE)
    source = models.CharField(max_length=140)
    geo = models.ForeignKey('Place', on_delete=models.CASCADE)
    like_count = models.IntegerField()
    quote_count = models.IntegerField()
    reply_count = models.IntegerField()
    retweet_count = models.IntegerField()


    def __str__(self):
        return self.text

class User(models.Model):
    id = models.AutoField(primary_key=True)
    pass

class Place(models.Model):
    id = models.AutoField(primary_key=True)
    pass

class Space(models.Model):
    id = models.AutoField(primary_key=True)
    pass

class Trend(models.Model):
    id = models.AutoField(primary_key=True)
    pass

class Media(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=300)
    pass

class UserList(models.Model):
    id = models.AutoField(primary_key=True)
    pass

class EditHistory(models.Model):
    id = models.AutoField(primary_key=True)
    pass

