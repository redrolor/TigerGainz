# Generated by Django 3.0.7 on 2021-01-07 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddyrequest', '0002_auto_20200814_1725'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buddyrequest',
            name='profile_picture',
        ),
        migrations.AddField(
            model_name='buddyrequest',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
