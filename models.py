import os
from django import forms
from django.core.validators import FileExtensionValidator
from django.db import models

# the models used - used for the posts and profile picture and comments data bases + forms (not the comments forms)


class ProfilePicture(models.Model):  # profile picture class
    def upload_function(instance, filename):
        return os.path.join(filename.split("-")[0], filename)
    file = models.ImageField(upload_to=upload_function, validators=[FileExtensionValidator(
        allowed_extensions=['png', 'jpg'])])
    username = models.CharField(max_length=100, blank=True, null=True)


class PictureForm(forms.ModelForm):  # profile picture form
    class Meta:
        model = ProfilePicture
        fields = ['file']


class Post(models.Model):  # post class
    def upload_function(instance, filename):
        return os.path.join(filename.split("-")[0], filename)
    text = models.TextField()
    file = models.FileField(upload_to=upload_function, validators=[FileExtensionValidator(
        allowed_extensions=['png', 'jpg', 'mp4'])])
    username = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(auto_now=True)


class PostForm(forms.ModelForm):  # post form
    class Meta:
        model = Post
        fields = ['text', 'file']


class Comment(models.Model):  # comment class
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    username = models.CharField(max_length=100, blank=True, null=True)
