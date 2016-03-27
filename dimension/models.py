# -*- coding: utf-8 -*-
from django.db import models

import jsonfield


class Dimension(models.Model):
    name = models.CharField(u'Name', max_length=200)
    parent = models.ForeignKey('self', verbose_name='parent', null=True, blank=True,
                               related_name='+')
    data = jsonfield.JSONField(default={})

    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        return u'{}'.format(self.name)

    def change_parent(self, new_parent, update_fields=None):
        update_fields = update_fields or ['parent', 'data']
        self.parent = new_parent
        new_path = []
        if new_parent:
            new_path = new_parent.get_path()
            new_path.append(new_parent.id)
        self.set_data('path', list(set(new_path)))
        self.save(update_fields=update_fields)

        # updating path in every location
        locations_qs = self.locations.all()
        for location in locations_qs:
            location.update_dimension_tags(self)

        # updating path in every child
        children_qs = Dimension.objects.filter(parent=self)
        for child in children_qs:
            child.change_parent(self, update_fields=['data'])

    def set_data(self, key, new_value):
        if isinstance(self.data, dict):
            d = self.data
        else:
            d = dict()

        d[key] = new_value
        self.data = d

    def get_data(self):
        if isinstance(self.data, dict):
            return self.data
        else:
            return dict()

    def get_path(self):
        return self.get_data().get('path', [])

    def save(self, **kwargs):
        if not self.id:
            path = []
            if self.parent and isinstance(self.parent, Dimension):
                path = self.parent.get_path()
                path.append(self.parent.id)
            self.set_data('path', path)

        super(Dimension, self).save(**kwargs)

