# Generated by Django 2.0.2 on 2018-03-19 06:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_signuplocation'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='signup_location',
            field=models.ForeignKey(default='98d88966-1bc3-4728-9d6d-1ebe92c51089', on_delete=django.db.models.deletion.CASCADE, to='app.SignupLocation'),
            preserve_default=False,
        ),
    ]
