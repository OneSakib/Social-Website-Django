# Generated by Django 4.0.3 on 2022-03-06 21:16

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('images', '0004_remove_image_users_like_image_users_like'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='users_like',
        ),
        migrations.AddField(
            model_name='image',
            name='users_like',
            field=models.ManyToManyField(null=True, related_name='images_like', to=settings.AUTH_USER_MODEL),
        ),
    ]
