# Generated by Django 3.0.4 on 2022-03-15 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Site', '0002_auto_20220315_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]
