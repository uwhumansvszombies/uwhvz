# Generated by Django 2.2.8 on 2019-12-30 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_remove_user_legacy_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='moderator',
            name='score',
            field=models.CharField(blank=True, max_length=180, null=True, verbose_name="Moderator 'score'. Can include letters. For fun."),
        ),
    ]
