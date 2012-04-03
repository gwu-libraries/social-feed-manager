# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'TrendWeekly.sequence_num'
        db.delete_column('ui_trendweekly', 'sequence_num')

        # Deleting field 'TrendDaily.sequence_num'
        db.delete_column('ui_trenddaily', 'sequence_num')

    def backwards(self, orm):
        # Adding field 'TrendWeekly.sequence_num'
        db.add_column('ui_trendweekly', 'sequence_num',
                      self.gf('django.db.models.fields.SmallIntegerField')(default=1),
                      keep_default=False)

        # Adding field 'TrendDaily.sequence_num'
        db.add_column('ui_trenddaily', 'sequence_num',
                      self.gf('django.db.models.fields.SmallIntegerField')(default=1),
                      keep_default=False)

    models = {
        'ui.status': {
            'Meta': {'ordering': "['-date_published']", 'object_name': 'Status'},
            'avatar_url': ('django.db.models.fields.TextField', [], {}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'date_published': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rule_match': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'rule_tag': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'status_id': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'summary': ('django.db.models.fields.TextField', [], {}),
            'user_id': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'ui.trenddaily': {
            'Meta': {'ordering': "['-date', 'name']", 'object_name': 'TrendDaily'},
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'events': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'promoted_content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'query': ('django.db.models.fields.TextField', [], {})
        },
        'ui.trendweekly': {
            'Meta': {'ordering': "['-date', 'name']", 'object_name': 'TrendWeekly'},
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'events': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'promoted_content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'query': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['ui']