# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TwitterUserItemUrl'
        db.create_table(u'ui_twitteruseritemurl', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='urls', to=orm['ui.TwitterUserItem'])),
            ('date_checked', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('start_url', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('expanded_url', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('history', self.gf('django.db.models.fields.TextField')(default='{}', blank=True)),
            ('final_url', self.gf('django.db.models.fields.TextField')(db_index=True)),
            ('final_status', self.gf('django.db.models.fields.IntegerField')(default=200, db_index=True)),
            ('final_headers', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('duration_seconds', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal(u'ui', ['TwitterUserItemUrl'])


    def backwards(self, orm):
        # Deleting model 'TwitterUserItemUrl'
        db.delete_table(u'ui_twitteruseritemurl')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'ui.twitterfilter': {
            'Meta': {'object_name': 'TwitterFilter'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'locations': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'people': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'words': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'ui.twitteruser': {
            'Meta': {'object_name': 'TwitterUser'},
            'date_last_checked': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'former_names': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'sets': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['ui.TwitterUserSet']", 'symmetrical': 'False', 'blank': 'True'}),
            'uid': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'})
        },
        u'ui.twitteruseritem': {
            'Meta': {'object_name': 'TwitterUserItem'},
            'date_published': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_json': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'item_text': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'place': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'source': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'twitter_id': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'unique': 'True'}),
            'twitter_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': u"orm['ui.TwitterUser']"})
        },
        u'ui.twitteruseritemurl': {
            'Meta': {'object_name': 'TwitterUserItemUrl'},
            'date_checked': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'duration_seconds': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'expanded_url': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'final_headers': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'final_status': ('django.db.models.fields.IntegerField', [], {'default': '200', 'db_index': 'True'}),
            'final_url': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'history': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'urls'", 'to': u"orm['ui.TwitterUserItem']"}),
            'start_url': ('django.db.models.fields.TextField', [], {'db_index': 'True'})
        },
        u'ui.twitteruserset': {
            'Meta': {'ordering': "['user', 'name']", 'unique_together': "(['user', 'name'],)", 'object_name': 'TwitterUserSet'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sets'", 'to': u"orm['auth.User']"})
        },
        u'ui.twitterusertimelineerror': {
            'Meta': {'object_name': 'TwitterUserTimelineError'},
            'error': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'errors'", 'to': u"orm['ui.TwitterUserTimelineJob']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['ui.TwitterUser']"})
        },
        u'ui.twitterusertimelinejob': {
            'Meta': {'object_name': 'TwitterUserTimelineJob'},
            'date_finished': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'date_started': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_added': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['ui']