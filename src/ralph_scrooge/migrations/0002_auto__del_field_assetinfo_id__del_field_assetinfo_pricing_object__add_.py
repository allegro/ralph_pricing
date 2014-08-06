# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'AssetInfo.id'
        db.delete_column(u'ralph_scrooge_assetinfo', 'id')

        # Deleting field 'AssetInfo.pricing_object'
        db.delete_column(u'ralph_scrooge_assetinfo', 'pricing_object_id')

        # Adding field 'AssetInfo.pricingobject_ptr'
        db.add_column(u'ralph_scrooge_assetinfo', 'pricingobject_ptr',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=0, to=orm['ralph_scrooge.PricingObject'], unique=True, primary_key=True),
                      keep_default=False)

        # Deleting field 'DailyVirtualInfo.id'
        db.delete_column(u'ralph_scrooge_dailyvirtualinfo', 'id')

        # Deleting field 'DailyVirtualInfo.daily_pricing_object'
        db.delete_column(u'ralph_scrooge_dailyvirtualinfo', 'daily_pricing_object_id')

        # Adding field 'DailyVirtualInfo.dailypricingobject_ptr'
        db.add_column(u'ralph_scrooge_dailyvirtualinfo', 'dailypricingobject_ptr',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=0, to=orm['ralph_scrooge.DailyPricingObject'], unique=True, primary_key=True),
                      keep_default=False)

        # Deleting field 'VirtualInfo.id'
        db.delete_column(u'ralph_scrooge_virtualinfo', 'id')

        # Deleting field 'VirtualInfo.pricing_object'
        db.delete_column(u'ralph_scrooge_virtualinfo', 'pricing_object_id')

        # Adding field 'VirtualInfo.pricingobject_ptr'
        db.add_column(u'ralph_scrooge_virtualinfo', 'pricingobject_ptr',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=0, to=orm['ralph_scrooge.PricingObject'], unique=True, primary_key=True),
                      keep_default=False)

        # Deleting field 'DailyAssetInfo.daily_pricing_object'
        db.delete_column(u'ralph_scrooge_dailyassetinfo', 'daily_pricing_object_id')

        # Deleting field 'DailyAssetInfo.date'
        db.delete_column(u'ralph_scrooge_dailyassetinfo', 'date')

        # Deleting field 'DailyAssetInfo.id'
        db.delete_column(u'ralph_scrooge_dailyassetinfo', 'id')

        # Adding field 'DailyAssetInfo.dailypricingobject_ptr'
        db.add_column(u'ralph_scrooge_dailyassetinfo', 'dailypricingobject_ptr',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=0, to=orm['ralph_scrooge.DailyPricingObject'], unique=True, primary_key=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'AssetInfo.id'
        db.add_column(u'ralph_scrooge_assetinfo', 'id',
                      self.gf('django.db.models.fields.AutoField')(default=0, primary_key=True),
                      keep_default=False)

        # Adding field 'AssetInfo.pricing_object'
        db.add_column(u'ralph_scrooge_assetinfo', 'pricing_object',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=0, related_name=u'asset_info', unique=True, to=orm['ralph_scrooge.PricingObject']),
                      keep_default=False)

        # Deleting field 'AssetInfo.pricingobject_ptr'
        db.delete_column(u'ralph_scrooge_assetinfo', 'pricingobject_ptr_id')

        # Adding field 'DailyVirtualInfo.id'
        db.add_column(u'ralph_scrooge_dailyvirtualinfo', 'id',
                      self.gf('django.db.models.fields.AutoField')(default=0, primary_key=True),
                      keep_default=False)

        # Adding field 'DailyVirtualInfo.daily_pricing_object'
        db.add_column(u'ralph_scrooge_dailyvirtualinfo', 'daily_pricing_object',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=0, related_name=u'daily_virtual', unique=True, to=orm['ralph_scrooge.DailyPricingObject']),
                      keep_default=False)

        # Deleting field 'DailyVirtualInfo.dailypricingobject_ptr'
        db.delete_column(u'ralph_scrooge_dailyvirtualinfo', 'dailypricingobject_ptr_id')

        # Adding field 'VirtualInfo.id'
        db.add_column(u'ralph_scrooge_virtualinfo', 'id',
                      self.gf('django.db.models.fields.AutoField')(default=0, primary_key=True),
                      keep_default=False)

        # Adding field 'VirtualInfo.pricing_object'
        db.add_column(u'ralph_scrooge_virtualinfo', 'pricing_object',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=0, related_name=u'virtual', unique=True, to=orm['ralph_scrooge.PricingObject']),
                      keep_default=False)

        # Deleting field 'VirtualInfo.pricingobject_ptr'
        db.delete_column(u'ralph_scrooge_virtualinfo', 'pricingobject_ptr_id')

        # Adding field 'DailyAssetInfo.daily_pricing_object'
        db.add_column(u'ralph_scrooge_dailyassetinfo', 'daily_pricing_object',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=0, related_name=u'daily_asset', unique=True, to=orm['ralph_scrooge.DailyPricingObject']),
                      keep_default=False)

        # Adding field 'DailyAssetInfo.date'
        db.add_column(u'ralph_scrooge_dailyassetinfo', 'date',
                      self.gf('django.db.models.fields.DateField')(default=0),
                      keep_default=False)

        # Adding field 'DailyAssetInfo.id'
        db.add_column(u'ralph_scrooge_dailyassetinfo', 'id',
                      self.gf('django.db.models.fields.AutoField')(default=0, primary_key=True),
                      keep_default=False)

        # Deleting field 'DailyAssetInfo.dailypricingobject_ptr'
        db.delete_column(u'ralph_scrooge_dailyassetinfo', 'dailypricingobject_ptr_id')


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
        u'ralph_scrooge.dailyextracost': {
            'Meta': {'object_name': 'DailyExtraCost'},
            'daily_pricing_object': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ralph_scrooge.DailyPricingObject']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remarks': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Service']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.ExtraCostType']"}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'ralph_scrooge.dailypricingobject': {
            'Meta': {'object_name': 'DailyPricingObject'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pricing_object': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.PricingObject']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_pricing_objects'", 'to': u"orm['ralph_scrooge.Service']"})
        },
        u'ralph_scrooge.dailyusage': {
            'Meta': {'object_name': 'DailyUsage'},
            'daily_pricing_object': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.DailyPricingObject']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remarks': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Service']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.UsageType']"}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'warehouse': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Warehouse']", 'null': 'True', 'on_delete': 'models.PROTECT'})
        },
        u'ralph_scrooge.dailyvirtualinfo': {
            'Meta': {'object_name': 'DailyVirtualInfo', '_ormbases': [u'ralph_scrooge.DailyPricingObject']},
            'dailypricingobject_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['ralph_scrooge.DailyPricingObject']", 'unique': 'True', 'primary_key': 'True'}),
            'hypervisor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'daily_virtuals'", 'to': u"orm['ralph_scrooge.DailyAssetInfo']"})
        },
        u'ralph_scrooge.extracost': {
            'Meta': {'object_name': 'ExtraCost'},
            'end': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'monthly_cost': ('django.db.models.fields.DecimalField', [], {'max_digits': '16', 'decimal_places': '6'}),
            'pricing_object': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['ralph_scrooge.PricingObject']", 'null': 'True', 'blank': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.Service']"}),
            'start': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ralph_scrooge.ExtraCostType']"})
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
            'business_line_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'ci_uid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by_id': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by_id': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
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
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pricing_objects'", 'to': u"orm['ralph_scrooge.Service']"}),
            'type': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'ralph_scrooge.pricingservice': {
            'Meta': {'object_name': 'PricingService'},
            'excluded_services': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'excluded_from_pricing_services'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['ralph_scrooge.Service']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'pricing_services'", 'symmetrical': 'False', 'to': u"orm['ralph_scrooge.Service']"}),
            'usage_types': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'services'", 'symmetrical': 'False', 'through': u"orm['ralph_scrooge.ServiceUsageTypes']", 'to': u"orm['ralph_scrooge.UsageType']"}),
            'use_universal_plugin': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'ralph_scrooge.service': {
            'Meta': {'object_name': 'Service'},
            'business_line': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'services'", 'null': 'True', 'to': u"orm['ralph_scrooge.BusinessLine']"}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'ci_uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'ownership': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'services'", 'symmetrical': 'False', 'through': u"orm['ralph_scrooge.ServiceOwnership']", 'to': u"orm['ralph_scrooge.Owner']"})
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
            'Meta': {'object_name': 'Team'},
            'billing_type': ('django.db.models.fields.CharField', [], {'default': "u'TIME'", 'max_length': '15'}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'excluded_services': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'excluded_teams'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['ralph_scrooge.Service']"}),
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
            'Meta': {'object_name': 'UsageType'},
            'average': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_cost': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_internet_provider': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_team': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_warehouse': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'divide_by': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'excluded_services': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'excluded_usage_types'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['ralph_scrooge.Service']"}),
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