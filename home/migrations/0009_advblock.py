# Generated by Django 3.0.8 on 2020-07-29 22:47

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0045_assign_unlock_grouppagepermission'),
        ('wagtailimages', '0022_uploadedimage'),
        ('home', '0008_node'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdvBlock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('title', models.CharField(blank=True, max_length=52, null=True)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('adv_link', models.URLField(blank=True, null=True)),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailimages.Image')),
                ('page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailcore.Page')),
                ('parental_page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='adv_block', to='home.HomePage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]