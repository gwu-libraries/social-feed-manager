# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding index on 'Status', fields ['date_published']
        db.create_index('ui_status', ['date_published'])


    def backwards(self, orm):
        
        # Removing index on 'Status', fields ['date_published']
        db.delete_index('ui_status', ['date_published'])


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
        }
    }

    complete_apps = ['ui']
