# Generated by Django 2.2.1 on 2020-05-03 18:32

from django.db import migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_auto_20200503_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='userRating',
            field=picklefield.fields.PickledObjectField(default={}, editable=False),
        ),
    ]
