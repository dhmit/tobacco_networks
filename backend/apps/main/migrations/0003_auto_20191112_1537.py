# Generated by Django 2.2.4 on 2019-11-12 15:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20191108_2333'),
    ]

    operations = [
        migrations.RenameField(
            model_name='djangoperson',
            old_name='position',
            new_name='most_likely_org',
        ),
    ]
