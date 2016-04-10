from dimension.models import Dimension


def retrieve_leaf_dimensions():
    query = ('SELECT n.id FROM dimension_dimension n WHERE NOT EXISTS '
             '(SELECT parent_id FROM dimension_dimension r WHERE r.parent_id = n.id)')

    ids = []
    for q in Dimension.objects.raw(query):
        ids.append(q.id)
    return Dimension.objects.filter(id__in=ids)