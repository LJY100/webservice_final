# Generated by Django 2.1 on 2018-09-11 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alert', '0007_auto_20180909_2121'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='board',
            name='board_update',
        ),
        migrations.AddField(
            model_name='board',
            name='board_alert',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]