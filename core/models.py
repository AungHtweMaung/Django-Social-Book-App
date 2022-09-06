import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings 
from datetime import datetime

# it will return the currently active user model if one is specified or User otherwise. 
User = get_user_model()

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_user = models.IntegerField(null=True, blank=True)
    bio = models.TextField(blank=True)
    profile_img = models.ImageField(upload_to="profile_images", default="blank-profile-picture.png")
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username


class Post(models.Model):
    # Admin panel ကနေ အကုန်ကြည့်ရအောင် လိုအပ်မယ့် field တွေထည့်ပေးထားတာ။ 
    # id သည် UUID ကိုသုံးထားလို့ 128 bits ရှိတဲ့ random objects တွေကို unique id တွေအနေနဲ့ generate လုပ်ပေးတယ် 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE) # user မရှိတော့ရင် အဲ့ user ရဲ့ post တွေလည်းမရှိတော့ဘူး
    
    # index in views.py မှာ FollowerCount table ထဲက name နဲ့ filter လုပ်ချင်လို့ post_owner ကိုထပ်ထည့်ပေးလိုက်တာ
    post_owner = models.CharField(max_length=100, null=True) 
    image = models.ImageField(upload_to="post_images")
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.id} (Author - {self.user})"
    
class LikePost(models.Model): 
    post_id = models.CharField(max_length=100)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self): 
        return self.user 

