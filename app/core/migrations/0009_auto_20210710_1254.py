# Generated by Django 3.2.5 on 2021-07-10 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_operation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operation',
            name='date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='operation',
            name='tags',
            field=models.ManyToManyField(null=True, to='core.Tag'),
        ),
    ]
