# Generated by Django 4.0.6 on 2022-08-14 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_alter_profile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='post_owner',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
