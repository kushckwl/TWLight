# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-02-03 16:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("users", "0049_auto_20191216_1742")]

    operations = [
        migrations.AddField(
            model_name="editor",
            name="wp_account_old_enough",
            field=models.BooleanField(
                default=False,
                editable=False,
                help_text="At their last login, did this user meet the account age criterion in the terms of use?",
            ),
        ),
        migrations.AddField(
            model_name="editor",
            name="wp_bundle_eligible",
            field=models.BooleanField(
                default=False,
                editable=False,
                help_text="At their last login, did this user meet the criteria for access to the library card bundle?",
            ),
        ),
        migrations.AddField(
            model_name="editor",
            name="wp_editcount_prev",
            field=models.IntegerField(
                blank=True,
                default=0,
                editable=False,
                help_text="Previous Wikipedia edit count",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="editor",
            name="wp_editcount_prev_updated",
            field=models.DateTimeField(
                blank=True,
                default=None,
                editable=False,
                help_text="When the previous editcount was last updated from Wikipedia",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="editor",
            name="wp_editcount_recent",
            field=models.IntegerField(
                blank=True,
                default=0,
                editable=False,
                help_text="Recent Wikipedia edit count",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="editor",
            name="wp_editcount_updated",
            field=models.DateTimeField(
                blank=True,
                default=None,
                editable=False,
                help_text="When the editcount was updated from Wikipedia",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="editor",
            name="wp_enough_edits",
            field=models.BooleanField(
                default=False,
                editable=False,
                help_text="At their last login, did this user meet the total editcount criterion in the terms of use?",
            ),
        ),
        migrations.AddField(
            model_name="editor",
            name="wp_enough_recent_edits",
            field=models.BooleanField(
                default=False,
                editable=False,
                help_text="At their last login, did this user meet the recent editcount criterion in the terms of use?",
            ),
        ),
        migrations.AddField(
            model_name="editor",
            name="wp_not_blocked",
            field=models.BooleanField(
                default=False,
                editable=False,
                help_text="At their last login, did this user meet the 'not currently blocked' criterion in the terms of use?",
            ),
        ),
        migrations.AlterField(
            model_name="editor",
            name="wp_valid",
            field=models.BooleanField(
                default=False,
                editable=False,
                help_text="At their last login, did this user meet the criteria in the terms of use?",
            ),
        ),
    ]