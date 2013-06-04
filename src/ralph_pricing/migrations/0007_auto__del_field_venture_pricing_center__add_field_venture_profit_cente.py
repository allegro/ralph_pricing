# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Venture.pricing_center'
        db.delete_column('ralph_pricing_venture', 'pricing_center')

        # Adding field 'Venture.profit_center'
        db.add_column('ralph_pricing_venture', 'profit_center',
                      self.gf('django.db.models.fields.CharField')(default=u'', max_length=75, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Venture.pricing_center'
        db.add_column('ralph_pricing_venture', 'pricing_center',
                      self.gf('django.db.models.fields.CharField')(default=u'', max_length=75, blank=True),
                      keep_default=False)

        # Deleting field 'Venture.profit_center'
        db.delete_column('ralph_pricing_venture', 'profit_center')


    models = {
        'ralph_pricing.dailydevice': {
            'Meta': {'unique_together': "((u'date', u'pricing_device'),)", 'object_name': 'DailyDevice'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'deprecation_rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deprecated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'child_set'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['ralph_pricing.Device']", 'blank': 'True', 'null': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'pricing_device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.Device']"}),
            'pricing_venture': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ralph_pricing.Venture']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'ralph_pricing.dailypart': {
            'Meta': {'ordering': "(u'asset_id', u'pricing_device', u'date')", 'unique_together': "((u'date', u'asset_id'),)", 'object_name': 'DailyPart'},
            'asset_id': ('django.db.models.fields.IntegerField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'deprecation_rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deprecated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'pricing_device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.Device']"})
        },
        'ralph_pricing.dailyusage': {
            'Meta': {'ordering': "(u'pricing_device', u'type', u'date')", 'unique_together': "((u'date', u'pricing_device', u'type'),)", 'object_name': 'DailyUsage'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pricing_device': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ralph_pricing.Device']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'pricing_venture': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ralph_pricing.Venture']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.UsageType']"}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'ralph_pricing.device': {
            'Meta': {'object_name': 'Device'},
            'asset_id': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'barcode': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'device_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_blade': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_virtual': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slots': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '200', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'ralph_pricing.extracost': {
            'Meta': {'unique_together': "[(u'start', u'pricing_venture', u'type'), (u'end', u'pricing_venture', u'type')]", 'object_name': 'ExtraCost'},
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '16', 'decimal_places': '6'}),
            'pricing_venture': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.Venture']"}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.ExtraCostType']"})
        },
        'ralph_pricing.extracosttype': {
            'Meta': {'object_name': 'ExtraCostType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'ralph_pricing.splunkname': {
            'Meta': {'unique_together': "((u'splunk_name', u'pricing_device'),)", 'object_name': 'SplunkName'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pricing_device': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ralph_pricing.Device']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'splunk_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'ralph_pricing.usageprice': {
            'Meta': {'ordering': "(u'type', u'start')", 'unique_together': "[(u'start', u'type'), (u'end', u'type')]", 'object_name': 'UsagePrice'},
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '16', 'decimal_places': '6'}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.UsageType']"})
        },
        'ralph_pricing.usagetype': {
            'Meta': {'object_name': 'UsageType'},
            'average': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'show_price_percentage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_value_percentage': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'ralph_pricing.venture': {
            'Meta': {'object_name': 'Venture'},
            'business_segment': ('django.db.models.fields.TextField', [], {'default': "u''", 'max_length': '75', 'blank': 'True'}),
            'department': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'default': 'None', 'related_name': "u'children'", 'null': 'True', 'blank': 'True', 'to': "orm['ralph_pricing.Venture']"}),
            'profit_center': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '75', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'symbol': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '32', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'venture_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['ralph_pricing']