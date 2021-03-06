# Generated by Django 3.0.8 on 2020-07-31 21:46

from django.db import migrations
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0015_auto_20200731_2136'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ReviewFeature',
        ),
        migrations.AlterModelOptions(
            name='reviewitem',
            options={},
        ),
        migrations.AlterField(
            model_name='reviewgalleryimage',
            name='page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_images', to='blog.ReviewItem'),
        ),
    ]
