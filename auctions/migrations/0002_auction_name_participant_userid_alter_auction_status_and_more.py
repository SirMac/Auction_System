# Generated by Django 5.0.3 on 2024-10-27 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='name',
            field=models.CharField(default='1', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='participant',
            name='userid',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='auction',
            name='status',
            field=models.CharField(default='opened', max_length=200),
        ),
        migrations.AlterField(
            model_name='item',
            name='subcategoryid',
            field=models.CharField(max_length=200),
        ),
    ]