# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Owner'
        db.create_table('ralph_scrooge_owner', (
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
        db.send_create_signal('ralph_scrooge', ['Owner'])

        # Adding model 'BusinessLine'
        db.create_table('ralph_scrooge_businessline', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=75, db_index=True)),
            ('ci_uid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal('ralph_scrooge', ['BusinessLine'])

        # Adding model 'ServiceOwnership'
        db.create_table('ralph_scrooge_serviceownership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Service'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ralph_scrooge.Owner'])),
            ('type', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal('ralph_scrooge', ['ServiceOwnership'])

        # Deleting field 'Service.symbol'
        db.delete_column('ralph_scrooge_service', 'symbol')

        # Adding field 'Service.ci_uid'
        db.add_column('ralph_scrooge_service', 'ci_uid',
                      self.gf('django.db.models.fields.CharField')(default=2, unique=True, max_length=100),
                      keep_default=False)

        # Adding field 'Service.business_line'
        db.add_column('ralph_scrooge_service', 'business_line',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=2, related_name=u'services', to=orm['ralph_scrooge.BusinessLine']),
                      keep_default=False)

        # Removing M2M table for field base_usage_types on 'Service'
        db.delete_table('ralph_scrooge_service_base_usage_types')

        # Removing M2M table for field regular_usage_types on 'Service'
        db.delete_table('ralph_scrooge_service_regular_usage_types')

        # Removing M2M table for field dependency on 'Service'
        db.delete_table('ralph_scrooge_service_dependency')


    def backwards(self, orm):
        # Deleting model 'Owner'
        db.delete_table('ralph_scrooge_owner')

        # Deleting model 'BusinessLine'
        db.delete_table('ralph_scrooge_businessline')

        # Deleting model 'ServiceOwnership'
        db.delete_table('ralph_scrooge_serviceownership')

        # Adding field 'Service.symbol'
        db.add_column('ralph_scrooge_service', 'symbol',
                      self.gf('django.db.models.fields.CharField')(default=u'', max_length=255, blank=True),
                      keep_default=False)

        # Deleting field 'Service.ci_uid'
        db.delete_column('ralph_scrooge_service', 'ci_uid')

        # Deleting field 'Service.business_line'
        db.delete_column('ralph_scrooge_service', 'business_line_id')

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
        'ralph_scrooge.businessline': {
            'Meta': {'object_name': 'BusinessLine'},
            'ci_uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'})
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
        'ralph_scrooge.owner': {
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
        'ralph_scrooge.service': {
            'Meta': {'object_name': 'Service'},
            'business_line': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'services'", 'to': "orm['ralph_scrooge.BusinessLine']"}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'ci_uid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'ownership': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'services'", 'symmetrical': 'False', 'through': "orm['ralph_scrooge.ServiceOwnership']", 'to': "orm['ralph_scrooge.Owner']"}),
            'usage_types': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'services'", 'symmetrical': 'False', 'through': "orm['ralph_scrooge.ServiceUsageTypes']", 'to': "orm['ralph_scrooge.UsageType']"}),
            'use_universal_plugin': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'ralph_scrooge.serviceownership': {
            'Meta': {'object_name': 'ServiceOwnership'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_scrooge.Owner']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_scrooge.Service']"}),
            'type': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
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