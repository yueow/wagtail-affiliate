# Generated by Django 3.0.8 on 2020-07-17 14:37

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='themecolorscheme',
            old_name='color',
            new_name='navbar_text_color',
        ),
        migrations.RenameField(
            model_name='themecolorscheme',
            old_name='slug',
            new_name='title',
        ),
        migrations.AddField(
            model_name='themecolorscheme',
            name='navbar_bg_color',
            field=colorfield.fields.ColorField(default='white', max_length=10),
        ),
    ]