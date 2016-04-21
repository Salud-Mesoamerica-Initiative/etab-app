# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'DimensionTag', fields ['name']
        db.delete_unique(u'dimension_dimensiontag', ['name'])


    def backwards(self, orm):
        # Adding unique constraint on 'DimensionTag', fields ['name']
        db.create_unique(u'dimension_dimensiontag', ['name'])


    models = {
        u'dimension.dimension': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Dimension'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True'}),
            'data': ('jsonfield.fields.JSONField', [], {'default': '{}'}),
            'dimension_tag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dimension.DimensionTag']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['dimension.Dimension']"})
        },
        u'dimension.dimensiontag': {
            'Meta': {'object_name': 'DimensionTag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'})
        }
    }

    complete_apps = ['dimension']