# Generated by Django 3.2.3 on 2021-06-29 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_apitest_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='apitest',
            name='url',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='apitest',
            name='gjson',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
