# Generated by Django 3.2.5 on 2021-07-10 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20210710_1254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operation',
            name='tags',
            field=models.ManyToManyField(to='core.Tag'),
        ),
    ]
