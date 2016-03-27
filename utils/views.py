import json

from django.http import Http404

class AJAXRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            self.data = self.request.POST.dict()
            return super(AJAXRequiredMixin, self).dispatch(request, *args, **kwargs)

        raise Http404
