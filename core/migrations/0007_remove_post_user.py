# Generated by Django 4.0.6 on 2022-08-09 03:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_post_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='user',
        ),
    ]
