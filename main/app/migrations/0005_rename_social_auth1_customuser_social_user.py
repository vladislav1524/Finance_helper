# Generated by Django 5.1 on 2024-09-18 14:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_customuser_social_auth1'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='social_auth1',
            new_name='social_user',
        ),
    ]