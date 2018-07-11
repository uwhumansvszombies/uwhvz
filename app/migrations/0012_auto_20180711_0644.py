# Generated by Django 2.0.7 on 2018-07-11 06:44

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_player_modifier'),
    ]

    operations = [
        migrations.RenameField(
            model_name='supplycode',
            old_name='modifier',
            new_name='point_modifier',
        ),
        migrations.RenameField(
            model_name='tag',
            old_name='modifier',
            new_name='point_modifier',
        ),
        migrations.AddField(
            model_name='faction',
            name='game',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='app.Game'),
        ),
        migrations.AlterField(
            model_name='user',
            name='date_joined',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date joined'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(error_messages={'unique': 'An account with that email address already exists.'}, help_text='Please enter a valid email address.', max_length=254, unique=True, verbose_name='Email address'),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=30, verbose_name='First name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Deselect this instead of deleting accounts.', verbose_name='Active'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='Staff status'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='Last name'),
        ),
    ]
