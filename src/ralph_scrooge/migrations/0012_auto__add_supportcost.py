# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SupportCost'
        db.create_table(u'ralph_scrooge_supportcost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('extra_cost_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.ExtraCostType'])),
            ('cost', self.gf('django.db.models.fields.DecimalField')(max_digits=16, decimal_places=6)),
            ('forecast_cost', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=16, decimal_places=6)),
            ('start', self.gf('django.db.models.fields.DateField')(default=None, null=True, blank=True)),
            ('end', self.gf('django.db.models.fields.DateField')(default=None, null=True, blank=True)),
            ('remarks', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('support_id', self.gf('django.db.models.fields.IntegerField')()),
            ('pricing_object', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.PricingObject'])),
        ))
        db.send_create_signal(u'ralph_scrooge', ['SupportCost'])


    def backwards(self, orm):
        # Deleting model 'SupportCost'
        db.delete_table(u'ralph_scrooge_supportcost')


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
            'segment': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
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
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'depth': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'forecast': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'pricing_object': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'daily_costs'", 'null': 'True', 'to': u"orm['ralph_scrooge.PricingObject']"}),
            'service_environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_costs'", 'to': u"orm['ralph_scrooge.ServiceEnvironment']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_costs'", 'to': u"orm['ralph_scrooge.BaseUsage']"}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
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
            'tenant_info': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_tenants'", 'to': u"orm['ralph_scrooge.TenantInfo']"})
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
            'remarks': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
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
            'manually_allocate_costs': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'pricing_service': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'+'", 'null': 'True', 'to': u"orm['ralph_scrooge.PricingService']"}),
            'profit_center': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "u'+'", 'to': u"orm['ralph_scrooge.ProfitCenter']"}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
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
            'model': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'pricing_objects'", 'null': 'True', 'to': u"orm['ralph_scrooge.PricingObjectModel']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'service_environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pricing_objects'", 'to': u"orm['ralph_scrooge.ServiceEnvironment']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'default': '255', 'related_name': "u'pricing_objects'", 'to': u"orm['ralph_scrooge.PricingObjectType']"})
        },
        u'ralph_scrooge.pricingobjectmodel': {
            'Meta': {'ordering': "[u'manufacturer', u'name']", 'object_name': 'PricingObjectModel'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'model_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'default': '255', 'related_name': "u'pricing_object_models'", 'to': u"orm['ralph_scrooge.PricingObjectType']"})
        },
        u'ralph_scrooge.pricingobjecttype': {
            'Meta': {'object_name': 'PricingObjectType'},
            'color': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'icon_class': ('django.db.models.fields.CharField', [], {'default': "u'fa-tasks'", 'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'ralph_scrooge.pricingservice': {
            'Meta': {'ordering': "[u'name']", 'object_name': 'PricingService', '_ormbases': [u'ralph_scrooge.BaseUsage']},
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
            'manually_allocate_costs': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ownership': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'services'", 'symmetrical': 'False', 'through': u"orm['ralph_scrooge.ServiceOwnership']", 'to': u"orm['ralph_scrooge.Owner']"}),
            'pricing_service': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'services'", 'null': 'True', 'to': u"orm['ralph_scrooge.PricingService']"}),
            'profit_center': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'related_name': "u'services'", 'to': u"orm['ralph_scrooge.ProfitCenter']"}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        u'ralph_scrooge.serviceenvironment': {
            'Meta': {'ordering': "[u'service__name', u'environment__name']", 'unique_together': "((u'service', u'environment'),)", 'object_name': 'ServiceEnvironment'},
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
        u'ralph_scrooge.supportcost': {
            'Meta': {'object_name': 'SupportCost'},
            'cost': ('django.db.models.fields.DecimalField', [], {'max_digits': '16', 'decimal_places': '6'}),
            'end': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'extra_cost_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.ExtraCostType']"}),
            'forecast_cost': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '16', 'decimal_places': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pricing_object': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.PricingObject']"}),
            'remarks': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'start': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'support_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'ralph_scrooge.syncstatus': {
            'Meta': {'unique_together': "((u'date', u'plugin'),)", 'object_name': 'SyncStatus'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'plugin': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'remarks': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
        u'ralph_scrooge.teammanager': {
            'Meta': {'unique_together': "((u'manager', u'team'),)", 'object_name': 'TeamManager'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manager': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Owner']"}),
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
            'device_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
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
