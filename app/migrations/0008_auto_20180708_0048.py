# Generated by Django 2.0.7 on 2018-07-08 00:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_dashboardpage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='code',
            field=models.CharField(max_length=6),
        ),
    ]
