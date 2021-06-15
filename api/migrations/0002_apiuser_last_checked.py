# Generated by Django 2.2.23 on 2021-06-15 01:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='apiuser',
            name='last_checked',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
    ]
