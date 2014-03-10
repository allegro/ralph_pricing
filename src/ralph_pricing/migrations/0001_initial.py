# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Device'
        db.create_table('ralph_pricing_device', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('device_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('asset_id', self.gf('django.db.models.fields.IntegerField')(default=None, unique=True, null=True, blank=True)),
            ('is_virtual', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_blade', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('slots', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal('ralph_pricing', ['Device'])

        # Adding model 'Venture'
        db.create_table('ralph_pricing_venture', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('venture_id', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255)),
            ('department', self.gf('django.db.models.fields.CharField')(default=u'', max_length=255)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(default=None, related_name=u'children', null=True, blank=True, to=orm['ralph_pricing.Venture'])),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('ralph_pricing', ['Venture'])

        # Adding model 'DailyPart'
        db.create_table('ralph_pricing_dailypart', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('pricing_device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_pricing.Device'])),
            ('asset_id', self.gf('django.db.models.fields.IntegerField')()),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=16, decimal_places=6)),
            ('is_deprecated', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ralph_pricing', ['DailyPart'])

        # Adding unique constraint on 'DailyPart', fields ['date', 'asset_id']
        db.create_unique('ralph_pricing_dailypart', ['date', 'asset_id'])

        # Adding model 'DailyDevice'
        db.create_table('ralph_pricing_dailydevice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('pricing_device', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_pricing.Device'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'child_set', on_delete=models.SET_NULL, default=None, to=orm['ralph_pricing.Device'], blank=True, null=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=6)),
            ('pricing_venture', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ralph_pricing.Venture'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('is_deprecated', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ralph_pricing', ['DailyDevice'])

        # Adding unique constraint on 'DailyDevice', fields ['date', 'pricing_device']
        db.create_unique('ralph_pricing_dailydevice', ['date', 'pricing_device_id'])

        # Adding model 'UsageType'
        db.create_table('ralph_pricing_usagetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('ralph_pricing', ['UsageType'])

        # Adding model 'UsagePrice'
        db.create_table('ralph_pricing_usageprice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_pricing.UsageType'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=16, decimal_places=6)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('ralph_pricing', ['UsagePrice'])

        # Adding unique constraint on 'UsagePrice', fields ['start', 'type']
        # db.create_unique('ralph_pricing_usageprice', ['start', 'type_id'])

        # Adding unique constraint on 'UsagePrice', fields ['end', 'type']
        # db.create_unique('ralph_pricing_usageprice', ['end', 'type_id'])

        # Adding model 'DailyUsage'
        db.create_table('ralph_pricing_dailyusage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('pricing_venture', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ralph_pricing.Venture'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('pricing_device', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['ralph_pricing.Device'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('value', self.gf('django.db.models.fields.FloatField')()),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_pricing.UsageType'])),
        ))
        db.send_create_signal('ralph_pricing', ['DailyUsage'])

        # Adding unique constraint on 'DailyUsage', fields ['date', 'pricing_device', 'type']
        db.create_unique('ralph_pricing_dailyusage', ['date', 'pricing_device_id', 'type_id'])

        # Adding model 'ExtraCostType'
        db.create_table('ralph_pricing_extracosttype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('ralph_pricing', ['ExtraCostType'])

        # Adding model 'ExtraCost'
        db.create_table('ralph_pricing_extracost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_pricing.ExtraCostType'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=16, decimal_places=6)),
            ('pricing_venture', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_pricing.Venture'])),
        ))
        db.send_create_signal('ralph_pricing', ['ExtraCost'])

        # Adding unique constraint on 'ExtraCost', fields ['start', 'pricing_venture', 'type']
        db.create_unique('ralph_pricing_extracost', ['start', 'pricing_venture_id', 'type_id'])

        # Adding unique constraint on 'ExtraCost', fields ['end', 'pricing_venture', 'type']
        db.create_unique('ralph_pricing_extracost', ['end', 'pricing_venture_id', 'type_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'ExtraCost', fields ['end', 'pricing_venture', 'type']
        db.delete_unique('ralph_pricing_extracost', ['end', 'pricing_venture_id', 'type_id'])

        # Removing unique constraint on 'ExtraCost', fields ['start', 'pricing_venture', 'type']
        db.delete_unique('ralph_pricing_extracost', ['start', 'pricing_venture_id', 'type_id'])

        # Removing unique constraint on 'DailyUsage', fields ['date', 'pricing_device', 'type']
        db.delete_unique('ralph_pricing_dailyusage', ['date', 'pricing_device_id', 'type_id'])

        # Removing unique constraint on 'UsagePrice', fields ['end', 'type']
        db.delete_unique('ralph_pricing_usageprice', ['end', 'type_id'])

        # Removing unique constraint on 'UsagePrice', fields ['start', 'type']
        db.delete_unique('ralph_pricing_usageprice', ['start', 'type_id'])

        # Removing unique constraint on 'DailyDevice', fields ['date', 'pricing_device']
        db.delete_unique('ralph_pricing_dailydevice', ['date', 'pricing_device_id'])

        # Removing unique constraint on 'DailyPart', fields ['date', 'asset_id']
        db.delete_unique('ralph_pricing_dailypart', ['date', 'asset_id'])

        # Deleting model 'Device'
        db.delete_table('ralph_pricing_device')

        # Deleting model 'Venture'
        db.delete_table('ralph_pricing_venture')

        # Deleting model 'DailyPart'
        db.delete_table('ralph_pricing_dailypart')

        # Deleting model 'DailyDevice'
        db.delete_table('ralph_pricing_dailydevice')

        # Deleting model 'UsageType'
        db.delete_table('ralph_pricing_usagetype')

        # Deleting model 'UsagePrice'
        db.delete_table('ralph_pricing_usageprice')

        # Deleting model 'DailyUsage'
        db.delete_table('ralph_pricing_dailyusage')

        # Deleting model 'ExtraCostType'
        db.delete_table('ralph_pricing_extracosttype')

        # Deleting model 'ExtraCost'
        db.delete_table('ralph_pricing_extracost')


    models = {
        'ralph_pricing.dailydevice': {
            'Meta': {'ordering': "(u'pricing_device', u'date')", 'unique_together': "((u'date', u'pricing_device'),)", 'object_name': 'DailyDevice'},
            'date': ('django.db.models.fields.DateField', [], {}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deprecated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '16', 'decimal_places': '6'}),
            'pricing_device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.Device']"})
        },
        'ralph_pricing.dailyusage': {
            'Meta': {'ordering': "(u'pricing_device', u'type', u'date')", 'unique_together': "((u'date', u'pricing_device', u'type'),)", 'object_name': 'DailyUsage'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pricing_device': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ralph_pricing.Device']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'pricing_venture': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ralph_pricing.Venture']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.UsageType']"}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        'ralph_pricing.device': {
            'Meta': {'object_name': 'Device'},
            'asset_id': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'device_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_blade': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_virtual': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slots': ('django.db.models.fields.FloatField', [], {'default': '0'})
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'ralph_pricing.venture': {
            'Meta': {'object_name': 'Venture'},
            'department': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'default': 'None', 'related_name': "u'children'", 'null': 'True', 'blank': 'True', 'to': "orm['ralph_pricing.Venture']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'venture_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['ralph_pricing']
