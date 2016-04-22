from django.forms import ModelChoiceField, ModelMultipleChoiceField


def _location_path(obj):
    path_qs = obj.dimensionpath_set.all().order_by('-level')
    name_list = list(path_qs.values_list('dimension__name', flat=True))
    name_list.append(obj.title)
    return '/'.join(name_list)


class LocationModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return _location_path(obj)


class LocationModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return _location_path(obj)