# Generated by Django 5.0.3 on 2024-11-03 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auction_name_participant_userid_alter_auction_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='username',
            field=models.CharField(default='-', max_length=200),
        ),
    ]
