# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BaseUsage'
        db.create_table(u'ralph_scrooge_baseusage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=75, db_index=True)),
            ('type', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'ralph_scrooge', ['BaseUsage'])

        # Adding model 'DailyCost'
        db.create_table(u'ralph_scrooge_dailycost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('depth', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('pricing_object', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'daily_costs', null=True, to=orm['ralph_scrooge.PricingObject'])),
            ('service_environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'daily_costs', to=orm['ralph_scrooge.ServiceEnvironment'])),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'daily_costs', to=orm['ralph_scrooge.BaseUsage'])),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('percent', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('cost', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'ralph_scrooge', ['DailyCost'])

        # Adding model 'ExtraCostType'
        db.create_table(u'ralph_scrooge_extracosttype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['ExtraCostType'])

        # Adding model 'ExtraCost'
        db.create_table(u'ralph_scrooge_extracost', (
            ('baseusage_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ralph_scrooge.BaseUsage'], unique=True, primary_key=True)),
            ('extra_cost_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.ExtraCostType'])),
            ('monthly_cost', self.gf('django.db.models.fields.DecimalField')(max_digits=16, decimal_places=6)),
            ('service_environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'extra_costs', to=orm['ralph_scrooge.ServiceEnvironment'])),
            ('pricing_object', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ralph_scrooge.PricingObject'], null=True, blank=True)),
            ('start', self.gf('django.db.models.fields.DateField')(default=None, null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateField')(default=None, null=True, blank=True)),
            ('mode', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['ExtraCost'])

        # Adding model 'DailyExtraCost'
        db.create_table(u'ralph_scrooge_dailyextracost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('service_environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'daily_extra_costs', to=orm['ralph_scrooge.ServiceEnvironment'])),
            ('daily_pricing_object', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ralph_scrooge.DailyPricingObject'], null=True, blank=True)),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.ExtraCostType'])),
            ('remarks', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['DailyExtraCost'])

        # Adding model 'Owner'
        db.create_table(u'ralph_scrooge_owner', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('cmdb_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, unique=True, null=True)),
            ('sAMAccountName', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['Owner'])

        # Adding model 'ServiceOwnership'
        db.create_table(u'ralph_scrooge_serviceownership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Service'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Owner'])),
            ('type', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['ServiceOwnership'])

        # Adding model 'PricingObject'
        db.create_table(u'ralph_scrooge_pricingobject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default=None, max_length=200, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('remarks', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('service_environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'pricing_objects', to=orm['ralph_scrooge.ServiceEnvironment'])),
        ))
        db.send_create_signal(u'ralph_scrooge', ['PricingObject'])

        # Adding model 'DailyPricingObject'
        db.create_table(u'ralph_scrooge_dailypricingobject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('pricing_object', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'daily_pricing_objects', to=orm['ralph_scrooge.PricingObject'])),
            ('service_environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'daily_pricing_objects', to=orm['ralph_scrooge.ServiceEnvironment'])),
        ))
        db.send_create_signal(u'ralph_scrooge', ['DailyPricingObject'])

        # Adding model 'AssetInfo'
        db.create_table(u'ralph_scrooge_assetinfo', (
            ('pricingobject_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ralph_scrooge.PricingObject'], unique=True, primary_key=True)),
            ('sn', self.gf('django.db.models.fields.CharField')(max_length=200, unique=True, null=True, blank=True)),
            ('barcode', self.gf('django.db.models.fields.CharField')(max_length=200, unique=True, null=True, blank=True)),
            ('device_id', self.gf('django.db.models.fields.IntegerField')(default=None, unique=True, null=True, blank=True)),
            ('asset_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('warehouse', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Warehouse'])),
        ))
        db.send_create_signal(u'ralph_scrooge', ['AssetInfo'])

        # Adding model 'DailyAssetInfo'
        db.create_table(u'ralph_scrooge_dailyassetinfo', (
            ('dailypricingobject_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ralph_scrooge.DailyPricingObject'], unique=True, primary_key=True)),
            ('asset_info', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.AssetInfo'])),
            ('depreciation_rate', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('is_depreciated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('daily_cost', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['DailyAssetInfo'])

        # Adding model 'VirtualInfo'
        db.create_table(u'ralph_scrooge_virtualinfo', (
            ('pricingobject_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ralph_scrooge.PricingObject'], unique=True, primary_key=True)),
            ('device_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['VirtualInfo'])

        # Adding model 'DailyVirtualInfo'
        db.create_table(u'ralph_scrooge_dailyvirtualinfo', (
            ('dailypricingobject_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ralph_scrooge.DailyPricingObject'], unique=True, primary_key=True)),
            ('hypervisor', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'daily_virtuals', to=orm['ralph_scrooge.DailyAssetInfo'])),
            ('virtual_info', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'daily_virtuals', to=orm['ralph_scrooge.VirtualInfo'])),
        ))
        db.send_create_signal(u'ralph_scrooge', ['DailyVirtualInfo'])

        # Adding model 'TenantInfo'
        db.create_table(u'ralph_scrooge_tenantinfo', (
            ('pricingobject_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ralph_scrooge.PricingObject'], unique=True, primary_key=True)),
            ('tenant_id', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['TenantInfo'])

        # Adding model 'DailyTenantInfo'
        db.create_table(u'ralph_scrooge_dailytenantinfo', (
            ('dailypricingobject_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ralph_scrooge.DailyPricingObject'], unique=True, primary_key=True)),
            ('tenant_info', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'daily_tenant', to=orm['ralph_scrooge.TenantInfo'])),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['DailyTenantInfo'])

        # Adding model 'InternetProvider'
        db.create_table(u'ralph_scrooge_internetprovider', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=75, db_index=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['InternetProvider'])

        # Adding model 'UsageType'
        db.create_table(u'ralph_scrooge_usagetype', (
            ('baseusage_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ralph_scrooge.BaseUsage'], unique=True, primary_key=True)),
            ('symbol', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255, blank=True)),
            ('average', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_value_percentage', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_price_percentage', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('by_warehouse', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('by_internet_provider', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_manually_type', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('by_cost', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_in_services_report', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('show_in_devices_report', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('divide_by', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('rounding', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('usage_type', self.gf('django.db.models.fields.CharField')(default=u'RU', max_length=2)),
            ('use_universal_plugin', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['UsageType'])

        # Adding M2M table for field excluded_services on 'UsageType'
        db.create_table(u'ralph_scrooge_usagetype_excluded_services', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('usagetype', models.ForeignKey(orm[u'ralph_scrooge.usagetype'], null=False)),
            ('service', models.ForeignKey(orm[u'ralph_scrooge.service'], null=False))
        ))
        db.create_unique(u'ralph_scrooge_usagetype_excluded_services', ['usagetype_id', 'service_id'])

        # Adding model 'UsagePrice'
        db.create_table(u'ralph_scrooge_usageprice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.UsageType'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('forecast_price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('cost', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=16, decimal_places=6)),
            ('forecast_cost', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=16, decimal_places=6)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('warehouse', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Warehouse'], null=True, on_delete=models.PROTECT, blank=True)),
            ('internet_provider', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.InternetProvider'], null=True, on_delete=models.PROTECT, blank=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['UsagePrice'])

        # Adding unique constraint on 'UsagePrice', fields ['warehouse', 'start', 'type']
        db.create_unique(u'ralph_scrooge_usageprice', ['warehouse_id', 'start', 'type_id'])

        # Adding unique constraint on 'UsagePrice', fields ['warehouse', 'end', 'type']
        db.create_unique(u'ralph_scrooge_usageprice', ['warehouse_id', 'end', 'type_id'])

        # Adding unique constraint on 'UsagePrice', fields ['internet_provider', 'start', 'type']
        db.create_unique(u'ralph_scrooge_usageprice', ['internet_provider_id', 'start', 'type_id'])

        # Adding unique constraint on 'UsagePrice', fields ['internet_provider', 'end', 'type']
        db.create_unique(u'ralph_scrooge_usageprice', ['internet_provider_id', 'end', 'type_id'])

        # Adding model 'DailyUsage'
        db.create_table(u'ralph_scrooge_dailyusage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('service_environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'daily_usages', to=orm['ralph_scrooge.ServiceEnvironment'])),
            ('daily_pricing_object', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.DailyPricingObject'])),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.UsageType'])),
            ('warehouse', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['ralph_scrooge.Warehouse'], on_delete=models.PROTECT)),
            ('remarks', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['DailyUsage'])

        # Adding model 'BusinessLine'
        db.create_table(u'ralph_scrooge_businessline', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=75, db_index=True)),
            ('ci_uid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['BusinessLine'])

        # Adding model 'Environment'
        db.create_table(u'ralph_scrooge_environment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=75, db_index=True)),
            ('environment_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['Environment'])

        # Adding model 'HistoricalService'
        db.create_table('ralph_scrooge_historicalservice', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('business_line', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name=u'+', to=orm['ralph_scrooge.BusinessLine'])),
            ('ci_uid', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('pricing_service', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'+', null=True, to=orm['ralph_scrooge.PricingService'])),
            (u'history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            (u'history_date', self.gf('django.db.models.fields.DateTimeField')()),
            (u'history_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            (u'history_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            (u'active_from', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            (u'active_to', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(9999, 12, 31, 0, 0))),
        ))
        db.send_create_signal('ralph_scrooge', ['HistoricalService'])

        # Adding model 'Service'
        db.create_table(u'ralph_scrooge_service', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('business_line', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name=u'services', to=orm['ralph_scrooge.BusinessLine'])),
            ('ci_uid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('pricing_service', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'services', null=True, to=orm['ralph_scrooge.PricingService'])),
        ))
        db.send_create_signal(u'ralph_scrooge', ['Service'])

        # Adding model 'PricingService'
        db.create_table(u'ralph_scrooge_pricingservice', (
            ('baseusage_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ralph_scrooge.BaseUsage'], unique=True, primary_key=True)),
            ('use_universal_plugin', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['PricingService'])

        # Adding M2M table for field excluded_services on 'PricingService'
        db.create_table(u'ralph_scrooge_pricingservice_excluded_services', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pricingservice', models.ForeignKey(orm[u'ralph_scrooge.pricingservice'], null=False)),
            ('service', models.ForeignKey(orm[u'ralph_scrooge.service'], null=False))
        ))
        db.create_unique(u'ralph_scrooge_pricingservice_excluded_services', ['pricingservice_id', 'service_id'])

        # Adding M2M table for field excluded_base_usage_types on 'PricingService'
        db.create_table(u'ralph_scrooge_pricingservice_excluded_base_usage_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pricingservice', models.ForeignKey(orm[u'ralph_scrooge.pricingservice'], null=False)),
            ('usagetype', models.ForeignKey(orm[u'ralph_scrooge.usagetype'], null=False))
        ))
        db.create_unique(u'ralph_scrooge_pricingservice_excluded_base_usage_types', ['pricingservice_id', 'usagetype_id'])

        # Adding M2M table for field regular_usage_types on 'PricingService'
        db.create_table(u'ralph_scrooge_pricingservice_regular_usage_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pricingservice', models.ForeignKey(orm[u'ralph_scrooge.pricingservice'], null=False)),
            ('usagetype', models.ForeignKey(orm[u'ralph_scrooge.usagetype'], null=False))
        ))
        db.create_unique(u'ralph_scrooge_pricingservice_regular_usage_types', ['pricingservice_id', 'usagetype_id'])

        # Adding model 'ServiceUsageTypes'
        db.create_table(u'ralph_scrooge_serviceusagetypes', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('usage_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'service_division', to=orm['ralph_scrooge.UsageType'])),
            ('pricing_service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.PricingService'])),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('percent', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'ralph_scrooge', ['ServiceUsageTypes'])

        # Adding model 'ServiceEnvironment'
        db.create_table(u'ralph_scrooge_serviceenvironment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'environments_services', to=orm['ralph_scrooge.Service'])),
            ('environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'services_environments', to=orm['ralph_scrooge.Environment'])),
        ))
        db.send_create_signal(u'ralph_scrooge', ['ServiceEnvironment'])

        # Adding model 'Statement'
        db.create_table(u'ralph_scrooge_statement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('header', self.gf('django.db.models.fields.TextField')()),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('forecast', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['Statement'])

        # Adding unique constraint on 'Statement', fields ['start', 'end', 'forecast', 'is_active']
        db.create_unique(u'ralph_scrooge_statement', ['start', 'end', 'forecast', 'is_active'])

        # Adding model 'Team'
        db.create_table(u'ralph_scrooge_team', (
            ('baseusage_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ralph_scrooge.BaseUsage'], unique=True, primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('show_in_report', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('show_percent_column', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('billing_type', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['Team'])

        # Adding M2M table for field excluded_services on 'Team'
        db.create_table(u'ralph_scrooge_team_excluded_services', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('team', models.ForeignKey(orm[u'ralph_scrooge.team'], null=False)),
            ('service', models.ForeignKey(orm[u'ralph_scrooge.service'], null=False))
        ))
        db.create_unique(u'ralph_scrooge_team_excluded_services', ['team_id', 'service_id'])

        # Adding model 'TeamCost'
        db.create_table(u'ralph_scrooge_teamcost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Team'])),
            ('members_count', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('cost', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=16, decimal_places=6)),
            ('forecast_cost', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=16, decimal_places=6)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'ralph_scrooge', ['TeamCost'])

        # Adding model 'TeamServiceEnvironmentPercent'
        db.create_table(u'ralph_scrooge_teamserviceenvironmentpercent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team_cost', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'percentage', to=orm['ralph_scrooge.TeamCost'])),
            ('service_environment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.ServiceEnvironment'])),
            ('percent', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'ralph_scrooge', ['TeamServiceEnvironmentPercent'])

        # Adding unique constraint on 'TeamServiceEnvironmentPercent', fields ['team_cost', 'service_environment']
        db.create_unique(u'ralph_scrooge_teamserviceenvironmentpercent', ['team_cost_id', 'service_environment_id'])

        # Adding model 'Warehouse'
        db.create_table(u'ralph_scrooge_warehouse', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=75, db_index=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('show_in_report', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id_from_assets', self.gf('django.db.models.fields.IntegerField')(unique=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['Warehouse'])


    def backwards(self, orm):
        # Removing unique constraint on 'TeamServiceEnvironmentPercent', fields ['team_cost', 'service_environment']
        db.delete_unique(u'ralph_scrooge_teamserviceenvironmentpercent', ['team_cost_id', 'service_environment_id'])

        # Removing unique constraint on 'Statement', fields ['start', 'end', 'forecast', 'is_active']
        db.delete_unique(u'ralph_scrooge_statement', ['start', 'end', 'forecast', 'is_active'])

        # Removing unique constraint on 'UsagePrice', fields ['internet_provider', 'end', 'type']
        db.delete_unique(u'ralph_scrooge_usageprice', ['internet_provider_id', 'end', 'type_id'])

        # Removing unique constraint on 'UsagePrice', fields ['internet_provider', 'start', 'type']
        db.delete_unique(u'ralph_scrooge_usageprice', ['internet_provider_id', 'start', 'type_id'])

        # Removing unique constraint on 'UsagePrice', fields ['warehouse', 'end', 'type']
        db.delete_unique(u'ralph_scrooge_usageprice', ['warehouse_id', 'end', 'type_id'])

        # Removing unique constraint on 'UsagePrice', fields ['warehouse', 'start', 'type']
        db.delete_unique(u'ralph_scrooge_usageprice', ['warehouse_id', 'start', 'type_id'])

        # Deleting model 'BaseUsage'
        db.delete_table(u'ralph_scrooge_baseusage')

        # Deleting model 'DailyCost'
        db.delete_table(u'ralph_scrooge_dailycost')

        # Deleting model 'ExtraCostType'
        db.delete_table(u'ralph_scrooge_extracosttype')

        # Deleting model 'ExtraCost'
        db.delete_table(u'ralph_scrooge_extracost')

        # Deleting model 'DailyExtraCost'
        db.delete_table(u'ralph_scrooge_dailyextracost')

        # Deleting model 'Owner'
        db.delete_table(u'ralph_scrooge_owner')

        # Deleting model 'ServiceOwnership'
        db.delete_table(u'ralph_scrooge_serviceownership')

        # Deleting model 'PricingObject'
        db.delete_table(u'ralph_scrooge_pricingobject')

        # Deleting model 'DailyPricingObject'
        db.delete_table(u'ralph_scrooge_dailypricingobject')

        # Deleting model 'AssetInfo'
        db.delete_table(u'ralph_scrooge_assetinfo')

        # Deleting model 'DailyAssetInfo'
        db.delete_table(u'ralph_scrooge_dailyassetinfo')

        # Deleting model 'VirtualInfo'
        db.delete_table(u'ralph_scrooge_virtualinfo')

        # Deleting model 'DailyVirtualInfo'
        db.delete_table(u'ralph_scrooge_dailyvirtualinfo')

        # Deleting model 'TenantInfo'
        db.delete_table(u'ralph_scrooge_tenantinfo')

        # Deleting model 'DailyTenantInfo'
        db.delete_table(u'ralph_scrooge_dailytenantinfo')

        # Deleting model 'InternetProvider'
        db.delete_table(u'ralph_scrooge_internetprovider')

        # Deleting model 'UsageType'
        db.delete_table(u'ralph_scrooge_usagetype')

        # Removing M2M table for field excluded_services on 'UsageType'
        db.delete_table('ralph_scrooge_usagetype_excluded_services')

        # Deleting model 'UsagePrice'
        db.delete_table(u'ralph_scrooge_usageprice')

        # Deleting model 'DailyUsage'
        db.delete_table(u'ralph_scrooge_dailyusage')

        # Deleting model 'BusinessLine'
        db.delete_table(u'ralph_scrooge_businessline')

        # Deleting model 'Environment'
        db.delete_table(u'ralph_scrooge_environment')

        # Deleting model 'HistoricalService'
        db.delete_table('ralph_scrooge_historicalservice')

        # Deleting model 'Service'
        db.delete_table(u'ralph_scrooge_service')

        # Deleting model 'PricingService'
        db.delete_table(u'ralph_scrooge_pricingservice')

        # Removing M2M table for field excluded_services on 'PricingService'
        db.delete_table('ralph_scrooge_pricingservice_excluded_services')

        # Removing M2M table for field excluded_base_usage_types on 'PricingService'
        db.delete_table('ralph_scrooge_pricingservice_excluded_base_usage_types')

        # Removing M2M table for field regular_usage_types on 'PricingService'
        db.delete_table('ralph_scrooge_pricingservice_regular_usage_types')

        # Deleting model 'ServiceUsageTypes'
        db.delete_table(u'ralph_scrooge_serviceusagetypes')

        # Deleting model 'ServiceEnvironment'
        db.delete_table(u'ralph_scrooge_serviceenvironment')

        # Deleting model 'Statement'
        db.delete_table(u'ralph_scrooge_statement')

        # Deleting model 'Team'
        db.delete_table(u'ralph_scrooge_team')

        # Removing M2M table for field excluded_services on 'Team'
        db.delete_table('ralph_scrooge_team_excluded_services')

        # Deleting model 'TeamCost'
        db.delete_table(u'ralph_scrooge_teamcost')

        # Deleting model 'TeamServiceEnvironmentPercent'
        db.delete_table(u'ralph_scrooge_teamserviceenvironmentpercent')

        # Deleting model 'Warehouse'
        db.delete_table(u'ralph_scrooge_warehouse')


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
        u'ralph_scrooge.assetinfo': {
            'Meta': {'object_name': 'AssetInfo', '_ormbases': [u'ralph_scrooge.PricingObject']},
            'asset_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'barcode': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'device_id': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'pricingobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ralph_scrooge.PricingObject']", 'unique': 'True', 'primary_key': 'True'}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'warehouse': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Warehouse']"})
        },
        u'ralph_scrooge.baseusage': {
            'Meta': {'object_name': 'BaseUsage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'type': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'ralph_scrooge.businessline': {
            'Meta': {'object_name': 'BusinessLine'},
            'ci_uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'})
        },
        u'ralph_scrooge.dailyassetinfo': {
            'Meta': {'object_name': 'DailyAssetInfo', '_ormbases': [u'ralph_scrooge.DailyPricingObject']},
            'asset_info': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.AssetInfo']"}),
            'daily_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'dailypricingobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ralph_scrooge.DailyPricingObject']", 'unique': 'True', 'primary_key': 'True'}),
            'depreciation_rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'is_depreciated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'})
        },
        u'ralph_scrooge.dailycost': {
            'Meta': {'object_name': 'DailyCost'},
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'percent': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'pricing_object': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'daily_costs'", 'null': 'True', 'to': u"orm['ralph_scrooge.PricingObject']"}),
            'service_environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_costs'", 'to': u"orm['ralph_scrooge.ServiceEnvironment']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_costs'", 'to': u"orm['ralph_scrooge.BaseUsage']"}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'ralph_scrooge.dailyextracost': {
            'Meta': {'object_name': 'DailyExtraCost'},
            'daily_pricing_object': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ralph_scrooge.DailyPricingObject']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remarks': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'service_environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_extra_costs'", 'to': u"orm['ralph_scrooge.ServiceEnvironment']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.ExtraCostType']"}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'ralph_scrooge.dailypricingobject': {
            'Meta': {'object_name': 'DailyPricingObject'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pricing_object': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_pricing_objects'", 'to': u"orm['ralph_scrooge.PricingObject']"}),
            'service_environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_pricing_objects'", 'to': u"orm['ralph_scrooge.ServiceEnvironment']"})
        },
        u'ralph_scrooge.dailytenantinfo': {
            'Meta': {'object_name': 'DailyTenantInfo', '_ormbases': [u'ralph_scrooge.DailyPricingObject']},
            'dailypricingobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ralph_scrooge.DailyPricingObject']", 'unique': 'True', 'primary_key': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tenant_info': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_tenant'", 'to': u"orm['ralph_scrooge.TenantInfo']"})
        },
        u'ralph_scrooge.dailyusage': {
            'Meta': {'object_name': 'DailyUsage'},
            'daily_pricing_object': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.DailyPricingObject']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remarks': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'service_environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_usages'", 'to': u"orm['ralph_scrooge.ServiceEnvironment']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.UsageType']"}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'warehouse': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['ralph_scrooge.Warehouse']", 'on_delete': 'models.PROTECT'})
        },
        u'ralph_scrooge.dailyvirtualinfo': {
            'Meta': {'object_name': 'DailyVirtualInfo', '_ormbases': [u'ralph_scrooge.DailyPricingObject']},
            'dailypricingobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ralph_scrooge.DailyPricingObject']", 'unique': 'True', 'primary_key': 'True'}),
            'hypervisor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_virtuals'", 'to': u"orm['ralph_scrooge.DailyAssetInfo']"}),
            'virtual_info': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_virtuals'", 'to': u"orm['ralph_scrooge.VirtualInfo']"})
        },
        u'ralph_scrooge.environment': {
            'Meta': {'ordering': "[u'name']", 'object_name': 'Environment'},
            'environment_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'})
        },
        u'ralph_scrooge.extracost': {
            'Meta': {'object_name': 'ExtraCost', '_ormbases': [u'ralph_scrooge.BaseUsage']},
            'baseusage_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ralph_scrooge.BaseUsage']", 'unique': 'True', 'primary_key': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'extra_cost_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.ExtraCostType']"}),
            'mode': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'monthly_cost': ('django.db.models.fields.DecimalField', [], {'max_digits': '16', 'decimal_places': '6'}),
            'pricing_object': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ralph_scrooge.PricingObject']", 'null': 'True', 'blank': 'True'}),
            'service_environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'extra_costs'", 'to': u"orm['ralph_scrooge.ServiceEnvironment']"}),
            'start': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        u'ralph_scrooge.extracosttype': {
            'Meta': {'object_name': 'ExtraCostType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'ralph_scrooge.historicalservice': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalService'},
            u'active_from': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'active_to': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(9999, 12, 31, 0, 0)'}),
            'business_line': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "u'+'", 'to': u"orm['ralph_scrooge.BusinessLine']"}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'ci_uid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'pricing_service': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'+'", 'null': 'True', 'to': u"orm['ralph_scrooge.PricingService']"})
        },
        u'ralph_scrooge.internetprovider': {
            'Meta': {'object_name': 'InternetProvider'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'})
        },
        u'ralph_scrooge.owner': {
            'Meta': {'object_name': 'Owner'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'cmdb_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'unique': 'True', 'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'sAMAccountName': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        },
        u'ralph_scrooge.pricingobject': {
            'Meta': {'object_name': 'PricingObject'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'service_environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pricing_objects'", 'to': u"orm['ralph_scrooge.ServiceEnvironment']"}),
            'type': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'ralph_scrooge.pricingservice': {
            'Meta': {'object_name': 'PricingService', '_ormbases': [u'ralph_scrooge.BaseUsage']},
            'baseusage_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ralph_scrooge.BaseUsage']", 'unique': 'True', 'primary_key': 'True'}),
            'excluded_base_usage_types': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'excluded_from_pricing_service'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['ralph_scrooge.UsageType']"}),
            'excluded_services': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'excluded_from_pricing_services'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['ralph_scrooge.Service']"}),
            'regular_usage_types': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'pricing_services'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['ralph_scrooge.UsageType']"}),
            'usage_types': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'services'", 'symmetrical': 'False', 'through': u"orm['ralph_scrooge.ServiceUsageTypes']", 'to': u"orm['ralph_scrooge.UsageType']"}),
            'use_universal_plugin': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'ralph_scrooge.service': {
            'Meta': {'ordering': "[u'name']", 'object_name': 'Service'},
            'business_line': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "u'services'", 'to': u"orm['ralph_scrooge.BusinessLine']"}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'ci_uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'environments': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'services'", 'symmetrical': 'False', 'through': u"orm['ralph_scrooge.ServiceEnvironment']", 'to': u"orm['ralph_scrooge.Environment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ownership': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'services'", 'symmetrical': 'False', 'through': u"orm['ralph_scrooge.ServiceOwnership']", 'to': u"orm['ralph_scrooge.Owner']"}),
            'pricing_service': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'services'", 'null': 'True', 'to': u"orm['ralph_scrooge.PricingService']"})
        },
        u'ralph_scrooge.serviceenvironment': {
            'Meta': {'object_name': 'ServiceEnvironment'},
            'environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'services_environments'", 'to': u"orm['ralph_scrooge.Environment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'environments_services'", 'to': u"orm['ralph_scrooge.Service']"})
        },
        u'ralph_scrooge.serviceownership': {
            'Meta': {'object_name': 'ServiceOwnership'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Owner']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Service']"}),
            'type': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        u'ralph_scrooge.serviceusagetypes': {
            'Meta': {'object_name': 'ServiceUsageTypes'},
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent': ('django.db.models.fields.FloatField', [], {}),
            'pricing_service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.PricingService']"}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'usage_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'service_division'", 'to': u"orm['ralph_scrooge.UsageType']"})
        },
        u'ralph_scrooge.statement': {
            'Meta': {'unique_together': "((u'start', u'end', u'forecast', u'is_active'),)", 'object_name': 'Statement'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'forecast': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'header': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start': ('django.db.models.fields.DateField', [], {})
        },
        u'ralph_scrooge.team': {
            'Meta': {'object_name': 'Team', '_ormbases': [u'ralph_scrooge.BaseUsage']},
            'baseusage_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ralph_scrooge.BaseUsage']", 'unique': 'True', 'primary_key': 'True'}),
            'billing_type': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'excluded_services': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'excluded_teams'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['ralph_scrooge.Service']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'show_in_report': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_percent_column': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'ralph_scrooge.teamcost': {
            'Meta': {'object_name': 'TeamCost'},
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '16', 'decimal_places': '6'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'forecast_cost': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '16', 'decimal_places': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Team']"})
        },
        u'ralph_scrooge.teamserviceenvironmentpercent': {
            'Meta': {'unique_together': "((u'team_cost', u'service_environment'),)", 'object_name': 'TeamServiceEnvironmentPercent'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent': ('django.db.models.fields.FloatField', [], {}),
            'service_environment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.ServiceEnvironment']"}),
            'team_cost': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'percentage'", 'to': u"orm['ralph_scrooge.TeamCost']"})
        },
        u'ralph_scrooge.tenantinfo': {
            'Meta': {'object_name': 'TenantInfo', '_ormbases': [u'ralph_scrooge.PricingObject']},
            'pricingobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ralph_scrooge.PricingObject']", 'unique': 'True', 'primary_key': 'True'}),
            'tenant_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        u'ralph_scrooge.usageprice': {
            'Meta': {'ordering': "(u'type', u'-start')", 'unique_together': "[(u'warehouse', u'start', u'type'), (u'warehouse', u'end', u'type'), (u'internet_provider', u'start', u'type'), (u'internet_provider', u'end', u'type')]", 'object_name': 'UsagePrice'},
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '16', 'decimal_places': '6'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'forecast_cost': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '16', 'decimal_places': '6'}),
            'forecast_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internet_provider': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.InternetProvider']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.UsageType']"}),
            'warehouse': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Warehouse']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'ralph_scrooge.usagetype': {
            'Meta': {'object_name': 'UsageType', '_ormbases': [u'ralph_scrooge.BaseUsage']},
            'average': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'baseusage_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ralph_scrooge.BaseUsage']", 'unique': 'True', 'primary_key': 'True'}),
            'by_cost': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_internet_provider': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_warehouse': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'divide_by': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'excluded_services': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'excluded_usage_types'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['ralph_scrooge.Service']"}),
            'is_manually_type': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rounding': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'show_in_devices_report': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_in_services_report': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_price_percentage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_value_percentage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'symbol': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'usage_type': ('django.db.models.fields.CharField', [], {'default': "u'RU'", 'max_length': '2'}),
            'use_universal_plugin': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'ralph_scrooge.virtualinfo': {
            'Meta': {'object_name': 'VirtualInfo', '_ormbases': [u'ralph_scrooge.PricingObject']},
            'device_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'pricingobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ralph_scrooge.PricingObject']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'ralph_scrooge.warehouse': {
            'Meta': {'object_name': 'Warehouse'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'id_from_assets': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'show_in_report': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['ralph_scrooge']