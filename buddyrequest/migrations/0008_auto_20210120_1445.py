# Generated by Django 3.0.7 on 2021-01-20 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buddyrequest', '0007_remove_buddyrequest_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buddyrequest',
            name='duration',
            field=models.IntegerField(null=True),
        ),
    ]