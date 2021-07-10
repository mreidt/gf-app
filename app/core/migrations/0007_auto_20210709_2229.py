# Generated by Django 3.2.5 on 2021-07-09 22:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='description',
            field=models.TextField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='tag',
            name='name',
            field=models.CharField(default='default', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tag',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.user'),
            preserve_default=False,
        ),
    ]