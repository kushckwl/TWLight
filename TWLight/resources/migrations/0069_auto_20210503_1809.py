# Generated by Django 3.1.8 on 2021-05-03 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("resources", "0068_partner_new_tags"),
    ]

    operations = [
        migrations.AlterField(
            model_name="partner",
            name="new_tags",
            field=models.JSONField(blank=True, default=None, null=True),
        ),
    ]
