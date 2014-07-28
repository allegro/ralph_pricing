# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Warehouse'
        db.create_table('ralph_scrooge_warehouse', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=75, db_index=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('show_in_report', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ralph_scrooge', ['Warehouse'])

        # Adding model 'InternetProvider'
        db.create_table('ralph_scrooge_internetprovider', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=75, db_index=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
        ))
        db.send_create_signal('ralph_scrooge', ['InternetProvider'])

        # Adding model 'Team'
        db.create_table('ralph_scrooge_team', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=75, db_index=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('show_in_report', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('show_percent_column', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('billing_type', self.gf('django.db.models.fields.CharField')(default=u'TIME', max_length=15)),
        ))
        db.send_create_signal('ralph_scrooge', ['Team'])

        # Adding M2M table for field excluded_ventures on 'Team'
        db.create_table('ralph_scrooge_team_excluded_ventures', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('team', models.ForeignKey(orm['ralph_scrooge.team'], null=False)),
            ('venture', models.ForeignKey(orm['ralph_scrooge.venture'], null=False))
        ))
        db.create_unique('ralph_scrooge_team_excluded_ventures', ['team_id', 'venture_id'])

        # Adding model 'TeamDaterange'
        db.create_table('ralph_scrooge_teamdaterange', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'dateranges', to=orm['ralph_scrooge.Team'])),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('ralph_scrooge', ['TeamDaterange'])

        # Adding model 'TeamVenturePercent'
        db.create_table('ralph_scrooge_teamventurepercent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team_daterange', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'percentage', to=orm['ralph_scrooge.TeamDaterange'])),
            ('venture', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Venture'])),
            ('percent', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('ralph_scrooge', ['TeamVenturePercent'])

        # Adding unique constraint on 'TeamVenturePercent', fields ['team_daterange', 'venture']
        db.create_unique('ralph_scrooge_teamventurepercent', ['team_daterange_id', 'venture_id'])

        # Adding model 'Statement'
        db.create_table('ralph_scrooge_statement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('header', self.gf('django.db.models.fields.TextField')()),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('forecast', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ralph_scrooge', ['Statement'])

        # Adding unique constraint on 'Statement', fields ['start', 'end', 'forecast', 'is_active']
        db.create_unique('ralph_scrooge_statement', ['start', 'end', 'forecast', 'is_active'])

        # Adding model 'UsageType'
        db.create_table('ralph_scrooge_usagetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('symbol', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255, blank=True)),
            ('average', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_value_percentage', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_price_percentage', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('by_warehouse', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('by_team', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('by_internet_provider', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_manually_type', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('by_cost', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_in_ventures_report', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('show_in_devices_report', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('divide_by', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('rounding', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('type', self.gf('django.db.models.fields.CharField')(default=u'RU', max_length=2)),
            ('use_universal_plugin', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('ralph_scrooge', ['UsageType'])

        # Adding M2M table for field excluded_ventures on 'UsageType'
        db.create_table('ralph_scrooge_usagetype_excluded_ventures', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('usagetype', models.ForeignKey(orm['ralph_scrooge.usagetype'], null=False)),
            ('venture', models.ForeignKey(orm['ralph_scrooge.venture'], null=False))
        ))
        db.create_unique('ralph_scrooge_usagetype_excluded_ventures', ['usagetype_id', 'venture_id'])

        # Adding model 'Service'
        db.create_table('ralph_scrooge_service', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=75, db_index=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('symbol', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255, blank=True)),
            ('use_universal_plugin', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('ralph_scrooge', ['Service'])

        # Adding M2M table for field base_usage_types on 'Service'
        db.create_table('ralph_scrooge_service_base_usage_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('service', models.ForeignKey(orm['ralph_scrooge.service'], null=False)),
            ('usagetype', models.ForeignKey(orm['ralph_scrooge.usagetype'], null=False))
        ))
        db.create_unique('ralph_scrooge_service_base_usage_types', ['service_id', 'usagetype_id'])

        # Adding M2M table for field regular_usage_types on 'Service'
        db.create_table('ralph_scrooge_service_regular_usage_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('service', models.ForeignKey(orm['ralph_scrooge.service'], null=False)),
            ('usagetype', models.ForeignKey(orm['ralph_scrooge.usagetype'], null=False))
        ))
        db.create_unique('ralph_scrooge_service_regular_usage_types', ['service_id', 'usagetype_id'])

        # Adding M2M table for field dependency on 'Service'
        db.create_table('ralph_scrooge_service_dependency', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_service', models.ForeignKey(orm['ralph_scrooge.service'], null=False)),
            ('to_service', models.ForeignKey(orm['ralph_scrooge.service'], null=False))
        ))
        db.create_unique('ralph_scrooge_service_dependency', ['from_service_id', 'to_service_id'])

        # Adding model 'ServiceUsageTypes'
        db.create_table('ralph_scrooge_serviceusagetypes', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('usage_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'service_division', to=orm['ralph_scrooge.UsageType'])),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Service'])),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('percent', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('ralph_scrooge', ['ServiceUsageTypes'])

        # Adding model 'Device'
        db.create_table('ralph_scrooge_device', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sn', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('barcode', self.gf('django.db.models.fields.CharField')(default=None, max_length=200, null=True, blank=True)),
            ('device_id', self.gf('django.db.models.fields.IntegerField')(default=None, unique=True, null=True, blank=True)),
            ('asset_id', self.gf('django.db.models.fields.IntegerField')(default=None, unique=True, null=True, blank=True)),
            ('is_virtual', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_blade', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('slots', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal('ralph_scrooge', ['Device'])

        # Adding model 'Venture'
        db.create_table('ralph_scrooge_venture', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('venture_id', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255)),
            ('department', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(default=None, related_name=u'children', null=True, blank=True, to=orm['ralph_scrooge.Venture'])),
            ('symbol', self.gf('django.db.models.fields.CharField')(default=u'', max_length=32, blank=True)),
            ('business_segment', self.gf('django.db.models.fields.TextField')(default=u'', max_length=75, blank=True)),
            ('profit_center', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Service'], null=True, blank=True)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('ralph_scrooge', ['Venture'])

        # Adding model 'DailyPart'
        db.create_table('ralph_scrooge_dailypart', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('pricing_device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Device'])),
            ('asset_id', self.gf('django.db.models.fields.IntegerField')()),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('deprecation_rate', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('is_deprecated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('daily_cost', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('monthly_cost', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
        ))
        db.send_create_signal('ralph_scrooge', ['DailyPart'])

        # Adding unique constraint on 'DailyPart', fields ['date', 'asset_id']
        db.create_unique('ralph_scrooge_dailypart', ['date', 'asset_id'])

        # Adding model 'DailyDevice'
        db.create_table('ralph_scrooge_dailydevice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('pricing_device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Device'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'child_set', on_delete=models.SET_NULL, default=None, to=orm['ralph_scrooge.Device'], blank=True, null=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('deprecation_rate', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('pricing_venture', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ralph_scrooge.Venture'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('is_deprecated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('daily_cost', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('monthly_cost', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
        ))
        db.send_create_signal('ralph_scrooge', ['DailyDevice'])

        # Adding unique constraint on 'DailyDevice', fields ['date', 'pricing_device']
        db.create_unique('ralph_scrooge_dailydevice', ['date', 'pricing_device_id'])

        # Adding model 'UsagePrice'
        db.create_table('ralph_scrooge_usageprice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.UsageType'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('forecast_price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('cost', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=16, decimal_places=6)),
            ('forecast_cost', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=16, decimal_places=6)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('warehouse', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Warehouse'], null=True, on_delete=models.PROTECT, blank=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Team'], null=True, on_delete=models.PROTECT, blank=True)),
            ('team_members_count', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('internet_provider', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.InternetProvider'], null=True, on_delete=models.PROTECT, blank=True)),
        ))
        db.send_create_signal('ralph_scrooge', ['UsagePrice'])

        # Adding unique constraint on 'UsagePrice', fields ['warehouse', 'start', 'type']
        db.create_unique('ralph_scrooge_usageprice', ['warehouse_id', 'start', 'type_id'])

        # Adding unique constraint on 'UsagePrice', fields ['warehouse', 'end', 'type']
        db.create_unique('ralph_scrooge_usageprice', ['warehouse_id', 'end', 'type_id'])

        # Adding unique constraint on 'UsagePrice', fields ['team', 'start', 'type']
        db.create_unique('ralph_scrooge_usageprice', ['team_id', 'start', 'type_id'])

        # Adding unique constraint on 'UsagePrice', fields ['team', 'end', 'type']
        db.create_unique('ralph_scrooge_usageprice', ['team_id', 'end', 'type_id'])

        # Adding unique constraint on 'UsagePrice', fields ['internet_provider', 'start', 'type']
        db.create_unique('ralph_scrooge_usageprice', ['internet_provider_id', 'start', 'type_id'])

        # Adding unique constraint on 'UsagePrice', fields ['internet_provider', 'end', 'type']
        db.create_unique('ralph_scrooge_usageprice', ['internet_provider_id', 'end', 'type_id'])

        # Adding model 'DailyUsage'
        db.create_table('ralph_scrooge_dailyusage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('pricing_venture', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ralph_scrooge.Venture'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('pricing_device', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ralph_scrooge.Device'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('total', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.UsageType'])),
            ('warehouse', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Warehouse'], null=True, on_delete=models.PROTECT)),
            ('remarks', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
        ))
        db.send_create_signal('ralph_scrooge', ['DailyUsage'])

        # Adding unique constraint on 'DailyUsage', fields ['date', 'pricing_device', 'type', 'pricing_venture']
        db.create_unique('ralph_scrooge_dailyusage', ['date', 'pricing_device_id', 'type_id', 'pricing_venture_id'])

        # Adding model 'ExtraCostType'
        db.create_table('ralph_scrooge_extracosttype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('ralph_scrooge', ['ExtraCostType'])

        # Adding model 'ExtraCost'
        db.create_table('ralph_scrooge_extracost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.ExtraCostType'])),
            ('monthly_cost', self.gf('django.db.models.fields.DecimalField')(max_digits=16, decimal_places=6)),
            ('pricing_venture', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Venture'])),
            ('pricing_device', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ralph_scrooge.Device'], null=True, blank=True)),
            ('start', self.gf('django.db.models.fields.DateField')(default=None, null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateField')(default=None, null=True, blank=True)),
            ('mode', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('ralph_scrooge', ['ExtraCost'])

        # Adding model 'DailyExtraCost'
        db.create_table('ralph_scrooge_dailyextracost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('pricing_venture', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Venture'])),
            ('pricing_device', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ralph_scrooge.Device'], null=True, blank=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.ExtraCostType'])),
            ('remarks', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
        ))
        db.send_create_signal('ralph_scrooge', ['DailyExtraCost'])

        # Adding unique constraint on 'DailyExtraCost', fields ['date', 'pricing_device', 'type', 'pricing_venture']
        db.create_unique('ralph_scrooge_dailyextracost', ['date', 'pricing_device_id', 'type_id', 'pricing_venture_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'DailyExtraCost', fields ['date', 'pricing_device', 'type', 'pricing_venture']
        db.delete_unique('ralph_scrooge_dailyextracost', ['date', 'pricing_device_id', 'type_id', 'pricing_venture_id'])

        # Removing unique constraint on 'DailyUsage', fields ['date', 'pricing_device', 'type', 'pricing_venture']
        db.delete_unique('ralph_scrooge_dailyusage', ['date', 'pricing_device_id', 'type_id', 'pricing_venture_id'])

        # Removing unique constraint on 'UsagePrice', fields ['internet_provider', 'end', 'type']
        db.delete_unique('ralph_scrooge_usageprice', ['internet_provider_id', 'end', 'type_id'])

        # Removing unique constraint on 'UsagePrice', fields ['internet_provider', 'start', 'type']
        db.delete_unique('ralph_scrooge_usageprice', ['internet_provider_id', 'start', 'type_id'])

        # Removing unique constraint on 'UsagePrice', fields ['team', 'end', 'type']
        db.delete_unique('ralph_scrooge_usageprice', ['team_id', 'end', 'type_id'])

        # Removing unique constraint on 'UsagePrice', fields ['team', 'start', 'type']
        db.delete_unique('ralph_scrooge_usageprice', ['team_id', 'start', 'type_id'])

        # Removing unique constraint on 'UsagePrice', fields ['warehouse', 'end', 'type']
        db.delete_unique('ralph_scrooge_usageprice', ['warehouse_id', 'end', 'type_id'])

        # Removing unique constraint on 'UsagePrice', fields ['warehouse', 'start', 'type']
        db.delete_unique('ralph_scrooge_usageprice', ['warehouse_id', 'start', 'type_id'])

        # Removing unique constraint on 'DailyDevice', fields ['date', 'pricing_device']
        db.delete_unique('ralph_scrooge_dailydevice', ['date', 'pricing_device_id'])

        # Removing unique constraint on 'DailyPart', fields ['date', 'asset_id']
        db.delete_unique('ralph_scrooge_dailypart', ['date', 'asset_id'])

        # Removing unique constraint on 'Statement', fields ['start', 'end', 'forecast', 'is_active']
        db.delete_unique('ralph_scrooge_statement', ['start', 'end', 'forecast', 'is_active'])

        # Removing unique constraint on 'TeamVenturePercent', fields ['team_daterange', 'venture']
        db.delete_unique('ralph_scrooge_teamventurepercent', ['team_daterange_id', 'venture_id'])

        # Deleting model 'Warehouse'
        db.delete_table('ralph_scrooge_warehouse')

        # Deleting model 'InternetProvider'
        db.delete_table('ralph_scrooge_internetprovider')

        # Deleting model 'Team'
        db.delete_table('ralph_scrooge_team')

        # Removing M2M table for field excluded_ventures on 'Team'
        db.delete_table('ralph_scrooge_team_excluded_ventures')

        # Deleting model 'TeamDaterange'
        db.delete_table('ralph_scrooge_teamdaterange')

        # Deleting model 'TeamVenturePercent'
        db.delete_table('ralph_scrooge_teamventurepercent')

        # Deleting model 'Statement'
        db.delete_table('ralph_scrooge_statement')

        # Deleting model 'UsageType'
        db.delete_table('ralph_scrooge_usagetype')

        # Removing M2M table for field excluded_ventures on 'UsageType'
        db.delete_table('ralph_scrooge_usagetype_excluded_ventures')

        # Deleting model 'Service'
        db.delete_table('ralph_scrooge_service')

        # Removing M2M table for field base_usage_types on 'Service'
        db.delete_table('ralph_scrooge_service_base_usage_types')

        # Removing M2M table for field regular_usage_types on 'Service'
        db.delete_table('ralph_scrooge_service_regular_usage_types')

        # Removing M2M table for field dependency on 'Service'
        db.delete_table('ralph_scrooge_service_dependency')

        # Deleting model 'ServiceUsageTypes'
        db.delete_table('ralph_scrooge_serviceusagetypes')

        # Deleting model 'Device'
        db.delete_table('ralph_scrooge_device')

        # Deleting model 'Venture'
        db.delete_table('ralph_scrooge_venture')

        # Deleting model 'DailyPart'
        db.delete_table('ralph_scrooge_dailypart')

        # Deleting model 'DailyDevice'
        db.delete_table('ralph_scrooge_dailydevice')

        # Deleting model 'UsagePrice'
        db.delete_table('ralph_scrooge_usageprice')

        # Deleting model 'DailyUsage'
        db.delete_table('ralph_scrooge_dailyusage')

        # Deleting model 'ExtraCostType'
        db.delete_table('ralph_scrooge_extracosttype')

        # Deleting model 'ExtraCost'
        db.delete_table('ralph_scrooge_extracost')

        # Deleting model 'DailyExtraCost'
        db.delete_table('ralph_scrooge_dailyextracost')


    models = {
        'account.profile': {
            'Meta': {'object_name': 'Profile'},
            'activation_token': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '40', 'blank': 'True'}),
            'birth_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'cost_center': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'country': ('django.db.models.fields.PositiveIntegerField', [], {'default': '153'}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'employee_id': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'gender': ('django.db.models.fields.PositiveIntegerField', [], {'default': '2'}),
            'home_page': (u'dj.choices.fields.ChoiceField', [], {'unique': 'False', 'primary_key': 'False', 'db_column': 'None', 'blank': 'False', u'default': '1', 'null': 'False', '_in_south': 'True', 'db_index': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_active': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'manager': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'nick': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '30', 'blank': 'True'}),
            'profit_center': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'time_zone': ('django.db.models.fields.FloatField', [], {'default': '1.0'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ralph_scrooge.dailydevice': {
            'Meta': {'unique_together': "((u'date', u'pricing_device'),)", 'object_name': 'DailyDevice'},
            'daily_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'deprecation_rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deprecated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'monthly_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'child_set'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['ralph_scrooge.Device']", 'blank': 'True', 'null': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'pricing_device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_scrooge.Device']"}),
            'pricing_venture': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ralph_scrooge.Venture']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'ralph_scrooge.dailyextracost': {
            'Meta': {'ordering': "(u'date', u'type', u'pricing_venture')", 'unique_together': "((u'date', u'pricing_device', u'type', u'pricing_venture'),)", 'object_name': 'DailyExtraCost'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pricing_device': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ralph_scrooge.Device']", 'null': 'True', 'blank': 'True'}),
            'pricing_venture': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_scrooge.Venture']"}),
            'remarks': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_scrooge.ExtraCostType']"}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'ralph_scrooge.dailypart': {
            'Meta': {'ordering': "(u'asset_id', u'pricing_device', u'date')", 'unique_together': "((u'date', u'asset_id'),)", 'object_name': 'DailyPart'},
            'asset_id': ('django.db.models.fields.IntegerField', [], {}),
            'daily_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'deprecation_rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deprecated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'monthly_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'pricing_device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_scrooge.Device']"})
        },
        'ralph_scrooge.dailyusage': {
            'Meta': {'unique_together': "((u'date', u'pricing_device', u'type', u'pricing_venture'),)", 'object_name': 'DailyUsage'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pricing_device': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ralph_scrooge.Device']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'pricing_venture': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ralph_scrooge.Venture']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'total': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_scrooge.UsageType']"}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'warehouse': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_scrooge.Warehouse']", 'null': 'True', 'on_delete': 'models.PROTECT'})
        },
        'ralph_scrooge.device': {
            'Meta': {'object_name': 'Device'},
            'asset_id': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'barcode': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'device_id': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_blade': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_virtual': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slots': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'ralph_scrooge.extracost': {
            'Meta': {'object_name': 'ExtraCost'},
            'end': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'monthly_cost': ('django.db.models.fields.DecimalField', [], {'max_digits': '16', 'decimal_places': '6'}),
            'pricing_device': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ralph_scrooge.Device']", 'null': 'True', 'blank': 'True'}),
            'pricing_venture': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_scrooge.Venture']"}),
            'start': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_scrooge.ExtraCostType']"})
        },
        'ralph_scrooge.extracosttype': {
            'Meta': {'object_name': 'ExtraCostType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'ralph_scrooge.internetprovider': {
            'Meta': {'object_name': 'InternetProvider'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'})
        },
        'ralph_scrooge.service': {
            'Meta': {'object_name': 'Service'},
            'base_usage_types': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'service_base_usage_types'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['ralph_scrooge.UsageType']"}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'dependency': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['ralph_scrooge.Service']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'regular_usage_types': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'service_regular_usage_types'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['ralph_scrooge.UsageType']"}),
            'symbol': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'usage_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ralph_scrooge.UsageType']", 'through': "orm['ralph_scrooge.ServiceUsageTypes']", 'symmetrical': 'False'}),
            'use_universal_plugin': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'ralph_scrooge.serviceusagetypes': {
            'Meta': {'object_name': 'ServiceUsageTypes'},
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent': ('django.db.models.fields.FloatField', [], {}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_scrooge.Service']"}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'usage_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'service_division'", 'to': "orm['ralph_scrooge.UsageType']"})
        },
        'ralph_scrooge.statement': {
            'Meta': {'unique_together': "((u'start', u'end', u'forecast', u'is_active'),)", 'object_name': 'Statement'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'forecast': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'header': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start': ('django.db.models.fields.DateField', [], {})
        },
        'ralph_scrooge.team': {
            'Meta': {'object_name': 'Team'},
            'billing_type': ('django.db.models.fields.CharField', [], {'default': "u'TIME'", 'max_length': '15'}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'excluded_ventures': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'+'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['ralph_scrooge.Venture']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'show_in_report': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_percent_column': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'ralph_scrooge.teamdaterange': {
            'Meta': {'object_name': 'TeamDaterange'},
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'dateranges'", 'to': "orm['ralph_scrooge.Team']"})
        },
        'ralph_scrooge.teamventurepercent': {
            'Meta': {'unique_together': "((u'team_daterange', u'venture'),)", 'object_name': 'TeamVenturePercent'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent': ('django.db.models.fields.FloatField', [], {}),
            'team_daterange': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'percentage'", 'to': "orm['ralph_scrooge.TeamDaterange']"}),
            'venture': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_scrooge.Venture']"})
        },
        'ralph_scrooge.usageprice': {
            'Meta': {'ordering': "(u'type', u'-start')", 'unique_together': "[(u'warehouse', u'start', u'type'), (u'warehouse', u'end', u'type'), (u'team', u'start', u'type'), (u'team', u'end', u'type'), (u'internet_provider', u'start', u'type'), (u'internet_provider', u'end', u'type')]", 'object_name': 'UsagePrice'},
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '16', 'decimal_places': '6'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'forecast_cost': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '16', 'decimal_places': '6'}),
            'forecast_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internet_provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_scrooge.InternetProvider']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_scrooge.Team']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'team_members_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_scrooge.UsageType']"}),
            'warehouse': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_scrooge.Warehouse']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        'ralph_scrooge.usagetype': {
            'Meta': {'object_name': 'UsageType'},
            'average': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_cost': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_internet_provider': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_team': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_warehouse': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'divide_by': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'excluded_ventures': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'excluded_usage_types'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['ralph_scrooge.Venture']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_manually_type': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rounding': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'show_in_devices_report': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_in_ventures_report': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_price_percentage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_value_percentage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'symbol': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "u'RU'", 'max_length': '2'}),
            'use_universal_plugin': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'ralph_scrooge.venture': {
            'Meta': {'ordering': "[u'name']", 'object_name': 'Venture'},
            'business_segment': ('django.db.models.fields.TextField', [], {'default': "u''", 'max_length': '75', 'blank': 'True'}),
            'department': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'default': 'None', 'related_name': "u'children'", 'null': 'True', 'blank': 'True', 'to': "orm['ralph_scrooge.Venture']"}),
            'profit_center': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_scrooge.Service']", 'null': 'True', 'blank': 'True'}),
            'symbol': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '32', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'venture_id': ('django.db.models.fields.IntegerField', [], {})
        },
        'ralph_scrooge.warehouse': {
            'Meta': {'object_name': 'Warehouse'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'show_in_report': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['ralph_scrooge']