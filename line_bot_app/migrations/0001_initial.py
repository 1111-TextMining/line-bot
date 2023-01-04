# Generated by Django 4.1.4 on 2023-01-03 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User_Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(default='', max_length=50)),
                ('mtext', models.CharField(blank=True, max_length=2000)),
                ('rtext', models.CharField(blank=True, max_length=2000)),
                ('ner_result', models.CharField(blank=True, max_length=2000)),
                ('mdt', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='User_Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(default='', max_length=50)),
                ('notes', models.CharField(blank=True, max_length=2000)),
                ('mdt', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
