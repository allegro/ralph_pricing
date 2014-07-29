# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'DailyUsage', fields ['date', 'pricing_venture', 'type', 'pricing_device']
        db.delete_unique('ralph_scrooge_dailyusage', ['date', 'pricing_venture_id', 'type_id', 'pricing_device_id'])

        # Removing unique constraint on 'DailyExtraCost', fields ['date', 'pricing_venture', 'type', 'pricing_device']
        db.delete_unique('ralph_scrooge_dailyextracost', ['date', 'pricing_venture_id', 'type_id', 'pricing_device_id'])

        # Removing unique constraint on 'DailyDevice', fields ['date', 'pricing_device']
        db.delete_unique('ralph_scrooge_dailydevice', ['date', 'pricing_device_id'])

        # Removing unique constraint on 'TeamVenturePercent', fields ['team_daterange', 'venture']
        db.delete_unique('ralph_scrooge_teamventurepercent', ['team_daterange_id', 'venture_id'])

        # Removing unique constraint on 'DailyPart', fields ['date', 'asset_id']
        db.delete_unique('ralph_scrooge_dailypart', ['date', 'asset_id'])

        # Deleting model 'DailyPart'
        db.delete_table('ralph_scrooge_dailypart')

        # Deleting model 'Device'
        db.delete_table('ralph_scrooge_device')

        # Deleting model 'TeamVenturePercent'
        db.delete_table('ralph_scrooge_teamventurepercent')

        # Deleting model 'Venture'
        db.delete_table('ralph_scrooge_venture')

        # Deleting model 'DailyDevice'
        db.delete_table('ralph_scrooge_dailydevice')

        # Adding model 'BaseModel'
        db.create_table(u'ralph_scrooge_basemodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['BaseModel'])

        # Adding model 'AssetInfo'
        db.create_table(u'ralph_scrooge_assetinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pricing_object', self.gf('django.db.models.fields.related.OneToOneField')(related_name=u'asset', unique=True, to=orm['ralph_scrooge.PricingObject'])),
            ('sn', self.gf('django.db.models.fields.CharField')(max_length=200, unique=True, null=True, blank=True)),
            ('barcode', self.gf('django.db.models.fields.CharField')(default=None, max_length=200, unique=True, null=True, blank=True)),
            ('device_id', self.gf('django.db.models.fields.IntegerField')(default=None, unique=True, null=True, blank=True)),
            ('asset_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['AssetInfo'])

        # Adding model 'DailyVirtualInfo'
        db.create_table(u'ralph_scrooge_dailyvirtualinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('daily_pricing_object', self.gf('django.db.models.fields.related.OneToOneField')(related_name=u'daily_virtual', unique=True, to=orm['ralph_scrooge.DailyPricingObject'])),
            ('hypervisor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.DailyAssetInfo'])),
        ))
        db.send_create_signal(u'ralph_scrooge', ['DailyVirtualInfo'])

        # Adding model 'VirtualInfo'
        db.create_table(u'ralph_scrooge_virtualinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pricing_object', self.gf('django.db.models.fields.related.OneToOneField')(related_name=u'virtual', unique=True, to=orm['ralph_scrooge.PricingObject'])),
            ('device_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['VirtualInfo'])

        # Adding model 'PricingObject'
        db.create_table(u'ralph_scrooge_pricingobject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=75, db_index=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm['account.Profile'], blank=True, null=True)),
            ('type', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('remarks', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'pricing_objects', to=orm['ralph_scrooge.Service'])),
        ))
        db.send_create_signal(u'ralph_scrooge', ['PricingObject'])

        # Adding model 'DailyAssetInfo'
        db.create_table(u'ralph_scrooge_dailyassetinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('daily_pricing_object', self.gf('django.db.models.fields.related.OneToOneField')(related_name=u'daily_asset', unique=True, to=orm['ralph_scrooge.DailyPricingObject'])),
            ('asset_info', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.AssetInfo'])),
            ('depreciation', self.gf('django.db.models.fields.IntegerField')()),
            ('daily_cost', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('is_depreciated', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'ralph_scrooge', ['DailyAssetInfo'])

        # Adding model 'TeamServicePercent'
        db.create_table(u'ralph_scrooge_teamservicepercent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('team_daterange', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'percentage', to=orm['ralph_scrooge.TeamDaterange'])),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Service'])),
            ('percent', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'ralph_scrooge', ['TeamServicePercent'])

        # Adding unique constraint on 'TeamServicePercent', fields ['team_daterange', 'service']
        db.create_unique(u'ralph_scrooge_teamservicepercent', ['team_daterange_id', 'service_id'])

        # Adding model 'DailyPricingObject'
        db.create_table(u'ralph_scrooge_dailypricingobject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pricing_object', self.gf('django.db.models.fields.related.OneToOneField')(related_name=u'daily_pricing_object', unique=True, to=orm['ralph_scrooge.PricingObject'])),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'daily_pricing_objects', to=orm['ralph_scrooge.Service'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'ralph_scrooge', ['DailyPricingObject'])

        # Deleting field 'DailyExtraCost.pricing_device'
        db.delete_column('ralph_scrooge_dailyextracost', 'pricing_device_id')

        # Deleting field 'DailyExtraCost.pricing_venture'
        db.delete_column('ralph_scrooge_dailyextracost', 'pricing_venture_id')

        # Adding field 'DailyExtraCost.asset'
        db.add_column(u'ralph_scrooge_dailyextracost', 'asset',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ralph_scrooge.AssetInfo'], null=True, blank=True),
                      keep_default=False)

        # Removing M2M table for field excluded_ventures on 'Team'
        db.delete_table('ralph_scrooge_team_excluded_ventures')

        # Adding M2M table for field excluded_services on 'Team'
        db.create_table(u'ralph_scrooge_team_excluded_services', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('team', models.ForeignKey(orm[u'ralph_scrooge.team'], null=False)),
            ('service', models.ForeignKey(orm[u'ralph_scrooge.service'], null=False))
        ))
        db.create_unique(u'ralph_scrooge_team_excluded_services', ['team_id', 'service_id'])

        # Deleting field 'ExtraCost.pricing_venture'
        db.delete_column('ralph_scrooge_extracost', 'pricing_venture_id')

        # Deleting field 'ExtraCost.pricing_device'
        db.delete_column('ralph_scrooge_extracost', 'pricing_device_id')

        # Adding field 'ExtraCost.asset'
        db.add_column(u'ralph_scrooge_extracost', 'asset',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ralph_scrooge.AssetInfo'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'DailyUsage.pricing_device'
        db.delete_column('ralph_scrooge_dailyusage', 'pricing_device_id')

        # Deleting field 'DailyUsage.pricing_venture'
        db.delete_column('ralph_scrooge_dailyusage', 'pricing_venture_id')

        # Adding field 'DailyUsage.pricing_object'
        db.add_column(u'ralph_scrooge_dailyusage', 'pricing_object',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['ralph_scrooge.PricingObject']),
                      keep_default=False)

        # Deleting field 'UsageType.id'
        db.delete_column('ralph_scrooge_usagetype', 'id')

        # Adding field 'UsageType.basemodel_ptr'
        db.add_column(u'ralph_scrooge_usagetype', 'basemodel_ptr',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=0, to=orm['ralph_scrooge.BaseModel'], unique=True, primary_key=True),
                      keep_default=False)

        # Removing M2M table for field excluded_ventures on 'UsageType'
        db.delete_table('ralph_scrooge_usagetype_excluded_ventures')


    def backwards(self, orm):
        # Removing unique constraint on 'TeamServicePercent', fields ['team_daterange', 'service']
        db.delete_unique(u'ralph_scrooge_teamservicepercent', ['team_daterange_id', 'service_id'])

        # Adding model 'DailyPart'
        db.create_table('ralph_scrooge_dailypart', (
            ('daily_cost', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('pricing_device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Device'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('deprecation_rate', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('asset_id', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('monthly_cost', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('is_deprecated', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ralph_scrooge', ['DailyPart'])

        # Adding unique constraint on 'DailyPart', fields ['date', 'asset_id']
        db.create_unique('ralph_scrooge_dailypart', ['date', 'asset_id'])

        # Adding model 'Device'
        db.create_table('ralph_scrooge_device', (
            ('asset_id', self.gf('django.db.models.fields.IntegerField')(default=None, unique=True, null=True, blank=True)),
            ('is_blade', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sn', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slots', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('barcode', self.gf('django.db.models.fields.CharField')(default=None, max_length=200, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_virtual', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('device_id', self.gf('django.db.models.fields.IntegerField')(default=None, unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('ralph_scrooge', ['Device'])

        # Adding model 'TeamVenturePercent'
        db.create_table('ralph_scrooge_teamventurepercent', (
            ('percent', self.gf('django.db.models.fields.FloatField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('venture', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Venture'])),
            ('team_daterange', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'percentage', to=orm['ralph_scrooge.TeamDaterange'])),
        ))
        db.send_create_signal('ralph_scrooge', ['TeamVenturePercent'])

        # Adding unique constraint on 'TeamVenturePercent', fields ['team_daterange', 'venture']
        db.create_unique('ralph_scrooge_teamventurepercent', ['team_daterange_id', 'venture_id'])

        # Adding model 'Venture'
        db.create_table('ralph_scrooge_venture', (
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(default=None, related_name=u'children', null=True, to=orm['ralph_scrooge.Venture'], blank=True)),
            ('venture_id', self.gf('django.db.models.fields.IntegerField')()),
            ('symbol', self.gf('django.db.models.fields.CharField')(default=u'', max_length=32, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('business_segment', self.gf('django.db.models.fields.TextField')(default=u'', max_length=75, blank=True)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Service'], null=True, blank=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('department', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255)),
            ('profit_center', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255, blank=True)),
        ))
        db.send_create_signal('ralph_scrooge', ['Venture'])

        # Adding model 'DailyDevice'
        db.create_table('ralph_scrooge_dailydevice', (
            ('daily_cost', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('pricing_device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Device'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'child_set', on_delete=models.SET_NULL, default=None, to=orm['ralph_scrooge.Device'], blank=True, null=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('deprecation_rate', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('monthly_cost', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('pricing_venture', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ralph_scrooge.Venture'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('is_deprecated', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ralph_scrooge', ['DailyDevice'])

        # Adding unique constraint on 'DailyDevice', fields ['date', 'pricing_device']
        db.create_unique('ralph_scrooge_dailydevice', ['date', 'pricing_device_id'])

        # Deleting model 'BaseModel'
        db.delete_table(u'ralph_scrooge_basemodel')

        # Deleting model 'AssetInfo'
        db.delete_table(u'ralph_scrooge_assetinfo')

        # Deleting model 'DailyVirtualInfo'
        db.delete_table(u'ralph_scrooge_dailyvirtualinfo')

        # Deleting model 'VirtualInfo'
        db.delete_table(u'ralph_scrooge_virtualinfo')

        # Deleting model 'PricingObject'
        db.delete_table(u'ralph_scrooge_pricingobject')

        # Deleting model 'DailyAssetInfo'
        db.delete_table(u'ralph_scrooge_dailyassetinfo')

        # Deleting model 'TeamServicePercent'
        db.delete_table(u'ralph_scrooge_teamservicepercent')

        # Deleting model 'DailyPricingObject'
        db.delete_table(u'ralph_scrooge_dailypricingobject')

        # Adding field 'DailyExtraCost.pricing_device'
        db.add_column('ralph_scrooge_dailyextracost', 'pricing_device',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ralph_scrooge.Device'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'DailyExtraCost.pricing_venture'
        db.add_column('ralph_scrooge_dailyextracost', 'pricing_venture',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['ralph_scrooge.Venture']),
                      keep_default=False)

        # Deleting field 'DailyExtraCost.asset'
        db.delete_column(u'ralph_scrooge_dailyextracost', 'asset_id')

        # Adding unique constraint on 'DailyExtraCost', fields ['date', 'pricing_venture', 'type', 'pricing_device']
        db.create_unique('ralph_scrooge_dailyextracost', ['date', 'pricing_venture_id', 'type_id', 'pricing_device_id'])

        # Adding M2M table for field excluded_ventures on 'Team'
        db.create_table('ralph_scrooge_team_excluded_ventures', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('team', models.ForeignKey(orm['ralph_scrooge.team'], null=False)),
            ('venture', models.ForeignKey(orm['ralph_scrooge.venture'], null=False))
        ))
        db.create_unique('ralph_scrooge_team_excluded_ventures', ['team_id', 'venture_id'])

        # Removing M2M table for field excluded_services on 'Team'
        db.delete_table('ralph_scrooge_team_excluded_services')

        # Adding field 'ExtraCost.pricing_venture'
        db.add_column('ralph_scrooge_extracost', 'pricing_venture',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['ralph_scrooge.Venture']),
                      keep_default=False)

        # Adding field 'ExtraCost.pricing_device'
        db.add_column('ralph_scrooge_extracost', 'pricing_device',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ralph_scrooge.Device'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'ExtraCost.asset'
        db.delete_column(u'ralph_scrooge_extracost', 'asset_id')

        # Adding field 'DailyUsage.pricing_device'
        db.add_column('ralph_scrooge_dailyusage', 'pricing_device',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ralph_scrooge.Device'], null=True, on_delete=models.SET_NULL, blank=True),
                      keep_default=False)

        # Adding field 'DailyUsage.pricing_venture'
        db.add_column('ralph_scrooge_dailyusage', 'pricing_venture',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ralph_scrooge.Venture'], null=True, on_delete=models.SET_NULL, blank=True),
                      keep_default=False)

        # Deleting field 'DailyUsage.pricing_object'
        db.delete_column(u'ralph_scrooge_dailyusage', 'pricing_object_id')

        # Adding unique constraint on 'DailyUsage', fields ['date', 'pricing_venture', 'type', 'pricing_device']
        db.create_unique('ralph_scrooge_dailyusage', ['date', 'pricing_venture_id', 'type_id', 'pricing_device_id'])

        # Adding field 'UsageType.id'
        db.add_column('ralph_scrooge_usagetype', 'id',
                      self.gf('django.db.models.fields.AutoField')(default=0, primary_key=True),
                      keep_default=False)

        # Deleting field 'UsageType.basemodel_ptr'
        db.delete_column(u'ralph_scrooge_usagetype', 'basemodel_ptr_id')

        # Adding M2M table for field excluded_ventures on 'UsageType'
        db.create_table('ralph_scrooge_usagetype_excluded_ventures', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('usagetype', models.ForeignKey(orm['ralph_scrooge.usagetype'], null=False)),
            ('venture', models.ForeignKey(orm['ralph_scrooge.venture'], null=False))
        ))
        db.create_unique('ralph_scrooge_usagetype_excluded_ventures', ['usagetype_id', 'venture_id'])


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
            'Meta': {'object_name': 'AssetInfo'},
            'asset_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'barcode': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'device_id': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pricing_object': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'asset'", 'unique': 'True', 'to': u"orm['ralph_scrooge.PricingObject']"}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'ralph_scrooge.basemodel': {
            'Meta': {'object_name': 'BaseModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'ralph_scrooge.businessline': {
            'Meta': {'object_name': 'BusinessLine'},
            'ci_uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'})
        },
        u'ralph_scrooge.dailyassetinfo': {
            'Meta': {'object_name': 'DailyAssetInfo'},
            'asset_info': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.AssetInfo']"}),
            'daily_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'daily_pricing_object': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'daily_asset'", 'unique': 'True', 'to': u"orm['ralph_scrooge.DailyPricingObject']"}),
            'depreciation': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_depreciated': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'ralph_scrooge.dailyextracost': {
            'Meta': {'ordering': "(u'date', u'type')", 'object_name': 'DailyExtraCost'},
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ralph_scrooge.AssetInfo']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remarks': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.ExtraCostType']"}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'ralph_scrooge.dailypricingobject': {
            'Meta': {'object_name': 'DailyPricingObject'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pricing_object': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'daily_pricing_object'", 'unique': 'True', 'to': u"orm['ralph_scrooge.PricingObject']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_pricing_objects'", 'to': u"orm['ralph_scrooge.Service']"})
        },
        u'ralph_scrooge.dailyusage': {
            'Meta': {'object_name': 'DailyUsage'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pricing_object': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.PricingObject']"}),
            'remarks': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'total': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.UsageType']"}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'warehouse': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Warehouse']", 'null': 'True', 'on_delete': 'models.PROTECT'})
        },
        u'ralph_scrooge.dailyvirtualinfo': {
            'Meta': {'object_name': 'DailyVirtualInfo'},
            'daily_pricing_object': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'daily_virtual'", 'unique': 'True', 'to': u"orm['ralph_scrooge.DailyPricingObject']"}),
            'hypervisor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.DailyAssetInfo']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'ralph_scrooge.extracost': {
            'Meta': {'object_name': 'ExtraCost'},
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ralph_scrooge.AssetInfo']", 'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'monthly_cost': ('django.db.models.fields.DecimalField', [], {'max_digits': '16', 'decimal_places': '6'}),
            'start': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.ExtraCostType']"})
        },
        u'ralph_scrooge.extracosttype': {
            'Meta': {'object_name': 'ExtraCostType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
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
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'remarks': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pricing_objects'", 'to': u"orm['ralph_scrooge.Service']"}),
            'type': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'ralph_scrooge.service': {
            'Meta': {'object_name': 'Service'},
            'business_line': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'services'", 'to': u"orm['ralph_scrooge.BusinessLine']"}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'ci_uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'ownership': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'services'", 'symmetrical': 'False', 'through': u"orm['ralph_scrooge.ServiceOwnership']", 'to': u"orm['ralph_scrooge.Owner']"}),
            'usage_types': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'services'", 'symmetrical': 'False', 'through': u"orm['ralph_scrooge.ServiceUsageTypes']", 'to': u"orm['ralph_scrooge.UsageType']"}),
            'use_universal_plugin': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'ralph_scrooge.serviceownership': {
            'Meta': {'object_name': 'ServiceOwnership'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Owner']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Service']"}),
            'type': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        u'ralph_scrooge.serviceusagetypes': {
            'Meta': {'object_name': 'ServiceUsageTypes'},
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent': ('django.db.models.fields.FloatField', [], {}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Service']"}),
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
            'Meta': {'object_name': 'Team'},
            'billing_type': ('django.db.models.fields.CharField', [], {'default': "u'TIME'", 'max_length': '15'}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'excluded_services': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'+'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['ralph_scrooge.Service']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'show_in_report': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_percent_column': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'ralph_scrooge.teamdaterange': {
            'Meta': {'object_name': 'TeamDaterange'},
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'dateranges'", 'to': u"orm['ralph_scrooge.Team']"})
        },
        u'ralph_scrooge.teamservicepercent': {
            'Meta': {'unique_together': "((u'team_daterange', u'service'),)", 'object_name': 'TeamServicePercent'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent': ('django.db.models.fields.FloatField', [], {}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Service']"}),
            'team_daterange': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'percentage'", 'to': u"orm['ralph_scrooge.TeamDaterange']"})
        },
        u'ralph_scrooge.usageprice': {
            'Meta': {'ordering': "(u'type', u'-start')", 'unique_together': "[(u'warehouse', u'start', u'type'), (u'warehouse', u'end', u'type'), (u'team', u'start', u'type'), (u'team', u'end', u'type'), (u'internet_provider', u'start', u'type'), (u'internet_provider', u'end', u'type')]", 'object_name': 'UsagePrice'},
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '16', 'decimal_places': '6'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'forecast_cost': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '16', 'decimal_places': '6'}),
            'forecast_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internet_provider': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.InternetProvider']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Team']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'team_members_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.UsageType']"}),
            'warehouse': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Warehouse']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        u'ralph_scrooge.usagetype': {
            'Meta': {'object_name': 'UsageType', '_ormbases': [u'ralph_scrooge.BaseModel']},
            'average': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'basemodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ralph_scrooge.BaseModel']", 'unique': 'True', 'primary_key': 'True'}),
            'by_cost': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_internet_provider': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_team': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_warehouse': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'divide_by': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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
        u'ralph_scrooge.virtualinfo': {
            'Meta': {'object_name': 'VirtualInfo'},
            'device_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pricing_object': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'virtual'", 'unique': 'True', 'to': u"orm['ralph_scrooge.PricingObject']"})
        },
        u'ralph_scrooge.warehouse': {
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