# Generated by Django 2.2.8 on 2019-12-30 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0030_auto_20191230_2043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moderator',
            name='score',
            field=models.CharField(blank=True, max_length=180, null=True, verbose_name="Moderator 'score'. Can include letters."),
        ),
    ]
