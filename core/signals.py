from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # instace သည် sender လာတဲ့ User object ကို ကိုယ်စားပြုတယ်
        # User object ထဲမှာ ရှိတဲ့ fields တွေကို instance ထဲက ခေါ်သုံးလို့ရတယ် 
        Profile.objects.create(user=instance, id_user=instance.id)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

