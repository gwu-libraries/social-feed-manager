# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Status'
        db.create_table('ui_status', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('date_published', self.gf('django.db.models.fields.DateTimeField')()),
            ('avatar_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('status_id', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('summary', self.gf('django.db.models.fields.TextField')()),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('rule_tag', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('rule_match', self.gf('django.db.models.fields.TextField')(db_index=True)),
        ))
        db.send_create_signal('ui', ['Status'])


    def backwards(self, orm):
        
        # Deleting model 'Status'
        db.delete_table('ui_status')


    models = {
        'ui.status': {
            'Meta': {'object_name': 'Status'},
            'avatar_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'date_published': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rule_match': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'rule_tag': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'status_id': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'summary': ('django.db.models.fields.TextField', [], {}),
            'user_id': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['ui']
