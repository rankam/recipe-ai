# Generated by Django 3.0.6 on 2020-05-20 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_auto_20200519_2322'),
    ]

    operations = [
        migrations.AddField(
            model_name='commoningredient',
            name='display_name',
            field=models.CharField(max_length=160, null=True),
        ),
    ]
