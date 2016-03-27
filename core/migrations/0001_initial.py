# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table(u'core_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal(u'core', ['UserProfile'])

        # Adding model 'Image'
        db.create_table(u'core_image', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'core_image_related', null=True, to=orm['auth.User'])),
            ('original_file', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('internal_file', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['Image'])

        # Adding model 'Location'
        db.create_table(u'core_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'core_location_related', null=True, to=orm['auth.User'])),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('position', self.gf('geoposition.fields.GeopositionField')(max_length=42)),
        ))
        db.send_create_signal(u'core', ['Location'])

        # Adding M2M table for field members on 'Location'
        m2m_table_name = db.shorten_name(u'core_location_members')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('location', models.ForeignKey(orm[u'core.location'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['location_id', 'user_id'])

        # Adding M2M table for field images on 'Location'
        m2m_table_name = db.shorten_name(u'core_location_images')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('location', models.ForeignKey(orm[u'core.location'], null=False)),
            ('image', models.ForeignKey(orm[u'core.image'], null=False))
        ))
        db.create_unique(m2m_table_name, ['location_id', 'image_id'])

        # Adding M2M table for field indicators on 'Location'
        m2m_table_name = db.shorten_name(u'core_location_indicators')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('location', models.ForeignKey(orm[u'core.location'], null=False)),
            ('indicator', models.ForeignKey(orm[u'core.indicator'], null=False))
        ))
        db.create_unique(m2m_table_name, ['location_id', 'indicator_id'])

        # Adding model 'Indicator'
        db.create_table(u'core_indicator', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('changed_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name=u'core_indicator_related', null=True, to=orm['auth.User'])),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['forms.Form'], unique=True, null=True, blank=True)),
            ('form_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('passing_percentage', self.gf('django.db.models.fields.FloatField')(default=85)),
            ('maximum_monthly_records', self.gf('django.db.models.fields.IntegerField')(default=20)),
        ))
        db.send_create_signal(u'core', ['Indicator'])

        # Adding model 'Score'
        db.create_table(u'core_score', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('indicator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Indicator'])),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Location'])),
            ('score', self.gf('django.db.models.fields.FloatField')(default=85)),
            ('passing', self.gf('django.db.models.fields.BooleanField')()),
            ('entry_count', self.gf('django.db.models.fields.IntegerField')()),
            ('passing_entry_count', self.gf('django.db.models.fields.IntegerField')()),
            ('month', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('year', self.gf('django.db.models.fields.IntegerField')()),
            ('datetime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['Score'])


    def backwards(self, orm):
        # Deleting model 'UserProfile'
        db.delete_table(u'core_userprofile')

        # Deleting model 'Image'
        db.delete_table(u'core_image')

        # Deleting model 'Location'
        db.delete_table(u'core_location')

        # Removing M2M table for field members on 'Location'
        db.delete_table(db.shorten_name(u'core_location_members'))

        # Removing M2M table for field images on 'Location'
        db.delete_table(db.shorten_name(u'core_location_images'))

        # Removing M2M table for field indicators on 'Location'
        db.delete_table(db.shorten_name(u'core_location_indicators'))

        # Deleting model 'Indicator'
        db.delete_table(u'core_indicator')

        # Deleting model 'Score'
        db.delete_table(u'core_score')


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
        u'core.image': {
            'Meta': {'object_name': 'Image'},
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'core_image_related'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'original_file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'core.indicator': {
            'Meta': {'object_name': 'Indicator'},
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'core_indicator_related'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['forms.Form']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'form_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maximum_monthly_records': ('django.db.models.fields.IntegerField', [], {'default': '20'}),
            'passing_percentage': ('django.db.models.fields.FloatField', [], {'default': '85'}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'core.location': {
            'Meta': {'object_name': 'Location'},
            'changed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'core_location_related'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'images': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['core.Image']", 'null': 'True', 'blank': 'True'}),
            'indicators': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['core.Indicator']", 'null': 'True', 'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'position': ('geoposition.fields.GeopositionField', [], {'max_length': '42'}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'core.score': {
            'Meta': {'object_name': 'Score'},
            'datetime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'entry_count': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Indicator']"}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Location']"}),
            'month': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'passing': ('django.db.models.fields.BooleanField', [], {}),
            'passing_entry_count': ('django.db.models.fields.IntegerField', [], {}),
            'score': ('django.db.models.fields.FloatField', [], {'default': '85'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        u'core.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'forms.form': {
            'Meta': {'object_name': 'Form'},
            'button_text': ('django.db.models.fields.CharField', [], {'default': "u'Submit'", 'max_length': '50'}),
            'email_copies': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'email_from': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'email_message': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_subject': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'expiry_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'response': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'send_email': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'default': '[1]', 'to': u"orm['sites.Site']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['core']