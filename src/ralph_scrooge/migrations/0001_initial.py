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
            ('symbol', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255, blank=True)),
            ('type', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('divide_by', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('rounding', self.gf('django.db.models.fields.IntegerField')(default=0)),
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
            ('warehouse', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'daily_costs', null=True, to=orm['ralph_scrooge.Warehouse'])),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('cost', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('forecast', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('verified', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'ralph_scrooge', ['DailyCost'])

        # Adding model 'CostDateStatus'
        db.create_table(u'ralph_scrooge_costdatestatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(unique=True)),
            ('calculated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('forecast_calculated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('accepted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('forecast_accepted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['CostDateStatus'])

        # Adding model 'ExtraCostType'
        db.create_table(u'ralph_scrooge_extracosttype', (
            ('baseusage_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ralph_scrooge.BaseUsage'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['ExtraCostType'])

        # Adding model 'ExtraCost'
        db.create_table(u'ralph_scrooge_extracost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('extra_cost_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.ExtraCostType'])),
            ('cost', self.gf('django.db.models.fields.DecimalField')(max_digits=16, decimal_places=6)),
            ('forecast_cost', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=16, decimal_places=6)),
            ('service_environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'extra_costs', to=orm['ralph_scrooge.ServiceEnvironment'])),
            ('start', self.gf('django.db.models.fields.DateField')(default=None, null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['ExtraCost'])

        # Adding model 'DynamicExtraCostType'
        db.create_table(u'ralph_scrooge_dynamicextracosttype', (
            ('baseusage_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ralph_scrooge.BaseUsage'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['DynamicExtraCostType'])

        # Adding M2M table for field excluded_services on 'DynamicExtraCostType'
        db.create_table(u'ralph_scrooge_dynamicextracosttype_excluded_services', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('dynamicextracosttype', models.ForeignKey(orm[u'ralph_scrooge.dynamicextracosttype'], null=False)),
            ('service', models.ForeignKey(orm[u'ralph_scrooge.service'], null=False))
        ))
        db.create_unique(u'ralph_scrooge_dynamicextracosttype_excluded_services', ['dynamicextracosttype_id', 'service_id'])

        # Adding model 'DynamicExtraCostDivision'
        db.create_table(u'ralph_scrooge_dynamicextracostdivision', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dynamic_extra_cost_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'division', to=orm['ralph_scrooge.DynamicExtraCostType'])),
            ('usage_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'dynamic_extra_cost_division', to=orm['ralph_scrooge.UsageType'])),
            ('percent', self.gf('django.db.models.fields.FloatField')(default=100)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['DynamicExtraCostDivision'])

        # Adding model 'DynamicExtraCost'
        db.create_table(u'ralph_scrooge_dynamicextracost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dynamic_extra_cost_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'costs', to=orm['ralph_scrooge.DynamicExtraCostType'])),
            ('cost', self.gf('django.db.models.fields.DecimalField')(max_digits=16, decimal_places=6)),
            ('forecast_cost', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=16, decimal_places=6)),
            ('start', self.gf('django.db.models.fields.DateField')(default=None, null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['DynamicExtraCost'])

        # Adding model 'Owner'
        db.create_table(u'ralph_scrooge_owner', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('cmdb_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('profile', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['account.Profile'], unique=True)),
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

        # Adding unique constraint on 'ServiceOwnership', fields ['owner', 'service', 'type']
        db.create_unique(u'ralph_scrooge_serviceownership', ['owner_id', 'service_id', 'type'])

        # Adding model 'PricingObject'
        db.create_table(u'ralph_scrooge_pricingobject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default=None, max_length=200, null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.PositiveIntegerField')(default=255)),
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

        # Adding unique constraint on 'DailyPricingObject', fields ['pricing_object', 'date']
        db.create_unique(u'ralph_scrooge_dailypricingobject', ['pricing_object_id', 'date'])

        # Adding model 'AssetInfo'
        db.create_table(u'ralph_scrooge_assetinfo', (
            ('pricingobject_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ralph_scrooge.PricingObject'], unique=True, primary_key=True)),
            ('sn', self.gf('django.db.models.fields.CharField')(max_length=200, unique=True, null=True, blank=True)),
            ('barcode', self.gf('django.db.models.fields.CharField')(max_length=200, unique=True, null=True, blank=True)),
            ('device_id', self.gf('django.db.models.fields.IntegerField')(default=None, unique=True, null=True, blank=True)),
            ('asset_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('warehouse', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Warehouse'])),
            ('model', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.AssetModel'])),
        ))
        db.send_create_signal(u'ralph_scrooge', ['AssetInfo'])

        # Adding model 'AssetModel'
        db.create_table(u'ralph_scrooge_assetmodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('model_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('manufacturer', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['AssetModel'])

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
            ('hypervisor', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'daily_virtuals', null=True, to=orm['ralph_scrooge.DailyAssetInfo'])),
            ('virtual_info', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'daily_virtuals', to=orm['ralph_scrooge.VirtualInfo'])),
        ))
        db.send_create_signal(u'ralph_scrooge', ['DailyVirtualInfo'])

        # Adding model 'TenantGroup'
        db.create_table(u'ralph_scrooge_tenantgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=75, db_index=True)),
            ('group_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'ralph_scrooge', ['TenantGroup'])

        # Adding model 'TenantInfo'
        db.create_table(u'ralph_scrooge_tenantinfo', (
            ('pricingobject_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ralph_scrooge.PricingObject'], unique=True, primary_key=True)),
            ('tenant_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100, db_index=True)),
            ('device_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'tenants', to=orm['ralph_scrooge.TenantGroup'])),
        ))
        db.send_create_signal(u'ralph_scrooge', ['TenantInfo'])

        # Adding model 'DailyTenantInfo'
        db.create_table(u'ralph_scrooge_dailytenantinfo', (
            ('dailypricingobject_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ralph_scrooge.DailyPricingObject'], unique=True, primary_key=True)),
            ('tenant_info', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'daily_tenant', to=orm['ralph_scrooge.TenantInfo'])),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['DailyTenantInfo'])

        # Adding model 'UsageType'
        db.create_table(u'ralph_scrooge_usagetype', (
            ('baseusage_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['ralph_scrooge.BaseUsage'], unique=True, primary_key=True)),
            ('average', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_value_percentage', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('by_warehouse', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_manually_type', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('by_cost', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_in_services_report', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('show_in_devices_report', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('usage_type', self.gf('django.db.models.fields.CharField')(default=u'SU', max_length=2)),
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
        ))
        db.send_create_signal(u'ralph_scrooge', ['UsagePrice'])

        # Adding model 'DailyUsage'
        db.create_table(u'ralph_scrooge_dailyusage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
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
            ('name', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('ci_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('ci_uid', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['BusinessLine'])

        # Adding model 'ProfitCenter'
        db.create_table(u'ralph_scrooge_profitcenter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('ci_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('ci_uid', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('business_line', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name=u'profit_centers', to=orm['ralph_scrooge.BusinessLine'])),
            ('description', self.gf('django.db.models.fields.TextField')(default=None, null=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['ProfitCenter'])

        # Adding model 'Environment'
        db.create_table(u'ralph_scrooge_environment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('ci_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('ci_uid', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
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
            ('ci_id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('ci_uid', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('profit_center', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name=u'+', to=orm['ralph_scrooge.ProfitCenter'])),
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
            ('ci_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('ci_uid', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('profit_center', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name=u'services', to=orm['ralph_scrooge.ProfitCenter'])),
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
            ('start', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(1, 1, 1, 0, 0))),
            ('end', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(9999, 12, 31, 0, 0))),
            ('percent', self.gf('django.db.models.fields.FloatField')(default=100)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['ServiceUsageTypes'])

        # Adding unique constraint on 'ServiceUsageTypes', fields ['usage_type', 'pricing_service', 'start', 'end']
        db.create_unique(u'ralph_scrooge_serviceusagetypes', ['usage_type_id', 'pricing_service_id', 'start', 'end'])

        # Adding model 'ServiceEnvironment'
        db.create_table(u'ralph_scrooge_serviceenvironment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'environments_services', to=orm['ralph_scrooge.Service'])),
            ('environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'services_environments', to=orm['ralph_scrooge.Environment'])),
        ))
        db.send_create_signal(u'ralph_scrooge', ['ServiceEnvironment'])

        # Adding unique constraint on 'ServiceEnvironment', fields ['service', 'environment']
        db.create_unique(u'ralph_scrooge_serviceenvironment', ['service_id', 'environment_id'])

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

        # Removing unique constraint on 'ServiceEnvironment', fields ['service', 'environment']
        db.delete_unique(u'ralph_scrooge_serviceenvironment', ['service_id', 'environment_id'])

        # Removing unique constraint on 'ServiceUsageTypes', fields ['usage_type', 'pricing_service', 'start', 'end']
        db.delete_unique(u'ralph_scrooge_serviceusagetypes', ['usage_type_id', 'pricing_service_id', 'start', 'end'])

        # Removing unique constraint on 'DailyPricingObject', fields ['pricing_object', 'date']
        db.delete_unique(u'ralph_scrooge_dailypricingobject', ['pricing_object_id', 'date'])

        # Removing unique constraint on 'ServiceOwnership', fields ['owner', 'service', 'type']
        db.delete_unique(u'ralph_scrooge_serviceownership', ['owner_id', 'service_id', 'type'])

        # Deleting model 'BaseUsage'
        db.delete_table(u'ralph_scrooge_baseusage')

        # Deleting model 'DailyCost'
        db.delete_table(u'ralph_scrooge_dailycost')

        # Deleting model 'CostDateStatus'
        db.delete_table(u'ralph_scrooge_costdatestatus')

        # Deleting model 'ExtraCostType'
        db.delete_table(u'ralph_scrooge_extracosttype')

        # Deleting model 'ExtraCost'
        db.delete_table(u'ralph_scrooge_extracost')

        # Deleting model 'DynamicExtraCostType'
        db.delete_table(u'ralph_scrooge_dynamicextracosttype')

        # Removing M2M table for field excluded_services on 'DynamicExtraCostType'
        db.delete_table('ralph_scrooge_dynamicextracosttype_excluded_services')

        # Deleting model 'DynamicExtraCostDivision'
        db.delete_table(u'ralph_scrooge_dynamicextracostdivision')

        # Deleting model 'DynamicExtraCost'
        db.delete_table(u'ralph_scrooge_dynamicextracost')

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

        # Deleting model 'AssetModel'
        db.delete_table(u'ralph_scrooge_assetmodel')

        # Deleting model 'DailyAssetInfo'
        db.delete_table(u'ralph_scrooge_dailyassetinfo')

        # Deleting model 'VirtualInfo'
        db.delete_table(u'ralph_scrooge_virtualinfo')

        # Deleting model 'DailyVirtualInfo'
        db.delete_table(u'ralph_scrooge_dailyvirtualinfo')

        # Deleting model 'TenantGroup'
        db.delete_table(u'ralph_scrooge_tenantgroup')

        # Deleting model 'TenantInfo'
        db.delete_table(u'ralph_scrooge_tenantinfo')

        # Deleting model 'DailyTenantInfo'
        db.delete_table(u'ralph_scrooge_dailytenantinfo')

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

        # Deleting model 'ProfitCenter'
        db.delete_table(u'ralph_scrooge_profitcenter')

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
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.AssetModel']"}),
            'pricingobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ralph_scrooge.PricingObject']", 'unique': 'True', 'primary_key': 'True'}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'warehouse': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Warehouse']"})
        },
        u'ralph_scrooge.assetmodel': {
            'Meta': {'ordering': "[u'manufacturer', u'name']", 'object_name': 'AssetModel'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'model_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'ralph_scrooge.baseusage': {
            'Meta': {'object_name': 'BaseUsage'},
            'divide_by': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'rounding': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'symbol': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'type': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'ralph_scrooge.businessline': {
            'Meta': {'object_name': 'BusinessLine'},
            'ci_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'ci_uid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'})
        },
        u'ralph_scrooge.costdatestatus': {
            'Meta': {'object_name': 'CostDateStatus'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'calculated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateField', [], {'unique': 'True'}),
            'forecast_accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'forecast_calculated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
            'forecast': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'pricing_object': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'daily_costs'", 'null': 'True', 'to': u"orm['ralph_scrooge.PricingObject']"}),
            'service_environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_costs'", 'to': u"orm['ralph_scrooge.ServiceEnvironment']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_costs'", 'to': u"orm['ralph_scrooge.BaseUsage']"}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'warehouse': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'daily_costs'", 'null': 'True', 'to': u"orm['ralph_scrooge.Warehouse']"})
        },
        u'ralph_scrooge.dailypricingobject': {
            'Meta': {'unique_together': "((u'pricing_object', u'date'),)", 'object_name': 'DailyPricingObject'},
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
            'date': ('django.db.models.fields.DateField', [], {}),
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
            'hypervisor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'daily_virtuals'", 'null': 'True', 'to': u"orm['ralph_scrooge.DailyAssetInfo']"}),
            'virtual_info': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_virtuals'", 'to': u"orm['ralph_scrooge.VirtualInfo']"})
        },
        u'ralph_scrooge.dynamicextracost': {
            'Meta': {'object_name': 'DynamicExtraCost'},
            'cost': ('django.db.models.fields.DecimalField', [], {'max_digits': '16', 'decimal_places': '6'}),
            'dynamic_extra_cost_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'costs'", 'to': u"orm['ralph_scrooge.DynamicExtraCostType']"}),
            'end': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'forecast_cost': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '16', 'decimal_places': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        u'ralph_scrooge.dynamicextracostdivision': {
            'Meta': {'object_name': 'DynamicExtraCostDivision'},
            'dynamic_extra_cost_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'division'", 'to': u"orm['ralph_scrooge.DynamicExtraCostType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent': ('django.db.models.fields.FloatField', [], {'default': '100'}),
            'usage_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'dynamic_extra_cost_division'", 'to': u"orm['ralph_scrooge.UsageType']"})
        },
        u'ralph_scrooge.dynamicextracosttype': {
            'Meta': {'object_name': 'DynamicExtraCostType', '_ormbases': [u'ralph_scrooge.BaseUsage']},
            'baseusage_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ralph_scrooge.BaseUsage']", 'unique': 'True', 'primary_key': 'True'}),
            'excluded_services': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'excluded_from_dynamic_usage_types'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['ralph_scrooge.Service']"})
        },
        u'ralph_scrooge.environment': {
            'Meta': {'ordering': "[u'name']", 'object_name': 'Environment'},
            'ci_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'ci_uid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'})
        },
        u'ralph_scrooge.extracost': {
            'Meta': {'object_name': 'ExtraCost'},
            'cost': ('django.db.models.fields.DecimalField', [], {'max_digits': '16', 'decimal_places': '6'}),
            'end': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'extra_cost_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.ExtraCostType']"}),
            'forecast_cost': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '16', 'decimal_places': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service_environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'extra_costs'", 'to': u"orm['ralph_scrooge.ServiceEnvironment']"}),
            'start': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        u'ralph_scrooge.extracosttype': {
            'Meta': {'object_name': 'ExtraCostType', '_ormbases': [u'ralph_scrooge.BaseUsage']},
            'baseusage_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ralph_scrooge.BaseUsage']", 'unique': 'True', 'primary_key': 'True'})
        },
        'ralph_scrooge.historicalservice': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalService'},
            u'active_from': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'active_to': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(9999, 12, 31, 0, 0)'}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'ci_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'ci_uid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
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
            'pricing_service': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'+'", 'null': 'True', 'to': u"orm['ralph_scrooge.PricingService']"}),
            'profit_center': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "u'+'", 'to': u"orm['ralph_scrooge.ProfitCenter']"})
        },
        u'ralph_scrooge.owner': {
            'Meta': {'ordering': "[u'profile__nick']", 'object_name': 'Owner'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'cmdb_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'profile': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['account.Profile']", 'unique': 'True'})
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
            'type': ('django.db.models.fields.PositiveIntegerField', [], {'default': '255'})
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
        u'ralph_scrooge.profitcenter': {
            'Meta': {'object_name': 'ProfitCenter'},
            'business_line': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "u'profit_centers'", 'to': u"orm['ralph_scrooge.BusinessLine']"}),
            'ci_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'ci_uid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'})
        },
        u'ralph_scrooge.service': {
            'Meta': {'ordering': "[u'name']", 'object_name': 'Service'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'ci_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'ci_uid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'environments': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'services'", 'symmetrical': 'False', 'through': u"orm['ralph_scrooge.ServiceEnvironment']", 'to': u"orm['ralph_scrooge.Environment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ownership': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'services'", 'symmetrical': 'False', 'through': u"orm['ralph_scrooge.ServiceOwnership']", 'to': u"orm['ralph_scrooge.Owner']"}),
            'pricing_service': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'services'", 'null': 'True', 'to': u"orm['ralph_scrooge.PricingService']"}),
            'profit_center': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "u'services'", 'to': u"orm['ralph_scrooge.ProfitCenter']"})
        },
        u'ralph_scrooge.serviceenvironment': {
            'Meta': {'unique_together': "((u'service', u'environment'),)", 'object_name': 'ServiceEnvironment'},
            'environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'services_environments'", 'to': u"orm['ralph_scrooge.Environment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'environments_services'", 'to': u"orm['ralph_scrooge.Service']"})
        },
        u'ralph_scrooge.serviceownership': {
            'Meta': {'unique_together': "((u'owner', u'service', u'type'),)", 'object_name': 'ServiceOwnership'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Owner']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Service']"}),
            'type': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        u'ralph_scrooge.serviceusagetypes': {
            'Meta': {'unique_together': "((u'usage_type', u'pricing_service', u'start', u'end'),)", 'object_name': 'ServiceUsageTypes'},
            'end': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(9999, 12, 31, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent': ('django.db.models.fields.FloatField', [], {'default': '100'}),
            'pricing_service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.PricingService']"}),
            'start': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(1, 1, 1, 0, 0)'}),
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
        u'ralph_scrooge.tenantgroup': {
            'Meta': {'object_name': 'TenantGroup'},
            'group_id': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'})
        },
        u'ralph_scrooge.tenantinfo': {
            'Meta': {'object_name': 'TenantInfo', '_ormbases': [u'ralph_scrooge.PricingObject']},
            'device_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'tenants'", 'to': u"orm['ralph_scrooge.TenantGroup']"}),
            'pricingobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ralph_scrooge.PricingObject']", 'unique': 'True', 'primary_key': 'True'}),
            'tenant_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'})
        },
        u'ralph_scrooge.usageprice': {
            'Meta': {'ordering': "(u'type', u'-start')", 'object_name': 'UsagePrice'},
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '16', 'decimal_places': '6'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'forecast_cost': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '16', 'decimal_places': '6'}),
            'forecast_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'by_warehouse': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'excluded_services': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'excluded_usage_types'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['ralph_scrooge.Service']"}),
            'is_manually_type': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'show_in_devices_report': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_in_services_report': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_value_percentage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'usage_type': ('django.db.models.fields.CharField', [], {'default': "u'SU'", 'max_length': '2'}),
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