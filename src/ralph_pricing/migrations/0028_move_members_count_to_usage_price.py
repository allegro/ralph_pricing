# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


class Migration(DataMigration):

    def forwards(self, orm):
        for team in orm.Team.objects.all():
            for members_count in team.teammemberscount_set.all():
                for usageprice in team.usageprice_set.filter(
                    start__gte=members_count.start,
                    end__lte=members_count.end,
                ):
                    usageprice.team_members_count = members_count.members_count
                    usageprice.save()

    def backwards(self, orm):
        for usageprice in orm.UsagePrice.objects.exclude(team_members_count=0):
            orm.TeamMembersCount.objects.get_or_create(
                start=usageprice.start,
                end=usageprice.end,
                team=usageprice.team,
                defaults=dict(
                    members_count=usageprice.team_members_count,
                )
            )

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
        'ralph_pricing.dailydevice': {
            'Meta': {'unique_together': "((u'date', u'pricing_device'),)", 'object_name': 'DailyDevice'},
            'daily_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'deprecation_rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deprecated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'monthly_cost': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'child_set'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['ralph_pricing.Device']", 'blank': 'True', 'null': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'pricing_device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.Device']"}),
            'pricing_venture': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ralph_pricing.Venture']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'ralph_pricing.dailypart': {
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
            'pricing_device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.Device']"})
        },
        'ralph_pricing.dailyusage': {
            'Meta': {'ordering': "(u'pricing_device', u'type', u'date')", 'unique_together': "((u'date', u'pricing_device', u'type', u'pricing_venture'),)", 'object_name': 'DailyUsage'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pricing_device': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ralph_pricing.Device']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'pricing_venture': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['ralph_pricing.Venture']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'remarks': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'total': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.UsageType']"}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'warehouse': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.Warehouse']", 'null': 'True', 'on_delete': 'models.PROTECT'})
        },
        'ralph_pricing.device': {
            'Meta': {'object_name': 'Device'},
            'asset_id': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'barcode': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'device_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_blade': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_virtual': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slots': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'sn': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
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
        'ralph_pricing.internetprovider': {
            'Meta': {'object_name': 'InternetProvider'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'})
        },
        'ralph_pricing.service': {
            'Meta': {'object_name': 'Service'},
            'base_usage_types': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'+'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['ralph_pricing.UsageType']"}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'dependency': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['ralph_pricing.Service']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'symbol': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'usage_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['ralph_pricing.UsageType']", 'through': "orm['ralph_pricing.ServiceUsageTypes']", 'symmetrical': 'False'}),
            'use_universal_plugin': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'ralph_pricing.serviceusagetypes': {
            'Meta': {'object_name': 'ServiceUsageTypes'},
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent': ('django.db.models.fields.FloatField', [], {}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.Service']"}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'usage_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'service_division'", 'to': "orm['ralph_pricing.UsageType']"})
        },
        'ralph_pricing.team': {
            'Meta': {'object_name': 'Team'},
            'billing_type': ('django.db.models.fields.CharField', [], {'default': "u'TIME'", 'max_length': '15'}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['account.Profile']", 'blank': 'True', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '75', 'db_index': 'True'}),
            'show_in_report': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'ralph_pricing.teamdaterange': {
            'Meta': {'object_name': 'TeamDaterange'},
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'dateranges'", 'to': "orm['ralph_pricing.Team']"})
        },
        'ralph_pricing.teammemberscount': {
            'Meta': {'object_name': 'TeamMembersCount'},
            'end': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.Team']"})
        },
        'ralph_pricing.teamventurepercent': {
            'Meta': {'unique_together': "((u'team_daterange', u'venture'),)", 'object_name': 'TeamVenturePercent'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent': ('django.db.models.fields.FloatField', [], {}),
            'team_daterange': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'percentage'", 'to': "orm['ralph_pricing.TeamDaterange']"}),
            'venture': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.Venture']"})
        },
        'ralph_pricing.usageprice': {
            'Meta': {'ordering': "(u'type', u'-start')", 'unique_together': "[(u'warehouse', u'start', u'type'), (u'warehouse', u'end', u'type'), (u'team', u'start', u'type'), (u'team', u'end', u'type'), (u'internet_provider', u'start', u'type'), (u'internet_provider', u'end', u'type')]", 'object_name': 'UsagePrice'},
            'cost': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '16', 'decimal_places': '6'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'forecast_cost': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '16', 'decimal_places': '6'}),
            'forecast_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internet_provider': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.InternetProvider']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '6'}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.Team']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'team_members_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.UsageType']"}),
            'warehouse': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.Warehouse']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'})
        },
        'ralph_pricing.usagetype': {
            'Meta': {'object_name': 'UsageType'},
            'average': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_cost': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_internet_provider': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_team': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'by_warehouse': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_manually_type': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'show_in_report': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_price_percentage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_value_percentage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'symbol': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "u'RU'", 'max_length': '2'}),
            'use_universal_plugin': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'ralph_pricing.venture': {
            'Meta': {'ordering': "[u'name']", 'object_name': 'Venture'},
            'business_segment': ('django.db.models.fields.TextField', [], {'default': "u''", 'max_length': '75', 'blank': 'True'}),
            'department': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '255'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'default': 'None', 'related_name': "u'children'", 'null': 'True', 'blank': 'True', 'to': "orm['ralph_pricing.Venture']"}),
            'profit_center': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '75', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ralph_pricing.Service']", 'null': 'True', 'blank': 'True'}),
            'symbol': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '32', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'venture_id': ('django.db.models.fields.IntegerField', [], {})
        },
        'ralph_pricing.warehouse': {
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

    complete_apps = ['ralph_pricing']
    symmetrical = True
