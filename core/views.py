from __future__ import unicode_literals

from uuid import uuid4

from carteblanche.mixins import NounView
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

# from core.verbs import NounView
import core.models as cm
import core.forms as cf
from actstream import action
import actstream.models as am
from django.contrib.auth import login, logout
import decimal
import forms_builder.forms.models as fm
from django.views.generic.edit import CreateView, UpdateView
import datetime, time
from dateutil.relativedelta import relativedelta
from django.utils import timezone


# do weird stuff to mAake user names nou usernames show up
def user_new_unicode(self):
    return self.get_full_name()


# Replace the __unicode__ method in the User class with out new implementation
User.__unicode__ = user_new_unicode


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)


class SiteRootView(NounView):
    def get_noun(self, **kwargs):
        siteroot = cm.SiteRoot()
        return siteroot


class MessageView(SiteRootView, TemplateView):
    template_name = 'base/messages.html'
    message = 'Message goes here.'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(MessageView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['message'] = self.message
        return context


class LandingView(SiteRootView, TemplateView):
    template_name = 'base/bootstrap.html'

    def get(self, request, **kwargs):
        # if the user has no payment methods, redirect to the view where one can be created
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse(viewname='location_list', current_app='core'))
        else:
            return super(LandingView, self).get(request, **kwargs)

        logout(self.request)


class BootstrapView(TemplateView):
    template_name = 'grid.html'


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.noun.pk,
            }
            return self.render_to_json_response(data)
        else:
            return response


class UserCreateView(SiteRootView, FormView):
    model = User
    template_name = 'base/form.html'
    form_class = cf.RegistrationForm

    def form_valid(self, form):
        user = User.objects.create_user(uuid4().hex[:30], form.cleaned_data['email'],
                                        form.cleaned_data['password1'])
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        self.object = user
        locations = form.cleaned_data['locations']
        for l in locations:
            l.members.add(user)
            l.save()
        return super(UserCreateView, self).form_valid(form)

    def get_success_url(self):
        action.send(self.request.user, verb='created user', action_object=self.object,
                    target=self.request.user)
        return reverse(viewname='make_new_user', current_app='core')

    def get_success_message(self, cleaned_data):
        first_name = cleaned_data['first_name']
        last_name = cleaned_data['last_name']
        locations = list(cleaned_data['locations'])
        location_names = ""
        if len(locations) > 0:
            for l in locations[:-1]:
                location_names += l.title + ", "
            location_names += " and " + locations[-1].title + "."
        else:
            location_names = "no locations."
        return first_name + " " + last_name + " now has an account. They are assigned to " + location_names + " Make another new user or return to the indicator."


class ProgressListView(SiteRootView, TemplateView):
    template_name = 'base/progress.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProgressListView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['locations'] = cm.Location.objects.filter(
            title__icontains=self.kwargs['tag']).order_by('title')
        return context


class UserLoginView(SiteRootView, FormView):
    template_name = 'base/form.html'
    form_class = cf.LoginForm
    success_url = '/'

    def form_valid(self, form):
        user = form.user_cache
        login(self.request, user)
        form.instance = user

        if self.request.is_ajax():
            context = {
                'status': 'success',
                'userid': user.id,
                'sessionid': self.request.session.session_key
            }
            data = json.dumps(context, default=decimal_default)
            out_kwargs = {'content_type': 'application/json'}
            return HttpResponse(data, **out_kwargs)
        else:
            return super(UserLoginView, self).form_valid(form)

    def form_invalid(self, form):
        response = super(UserLoginView, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response({"errors": form.errors, "status": "failure",})
        else:
            return response

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)


class UserView(NounView):
    def get_noun(self, **kwargs):
        user = User.objects.get(id=self.kwargs['pk'])
        coreuser = cm.CoreUser(user)
        user.required_verbs = coreuser.verb_classes
        user.get_verbs = coreuser.get_verbs
        user.get_available_verbs = coreuser.get_available_verbs
        user.conditions = coreuser.conditions
        return user


class UserDetailView(UserView, TemplateView):
    model = User
    template_name = 'base/bootstrap.html'


class UserPasswordResetView(UserView, FormView):
    model = User
    template_name = 'base/form.html'
    form_class = cf.PasswordResetForm

    def form_valid(self, form):
        user = User.objects.get(id=self.kwargs['pk'])
        password = form.cleaned_data['password1']
        user.set_password(password)
        user.save()
        return super(UserPasswordResetView, self).form_valid(form)

    def get_success_url(self):
        return reverse(viewname='user_list', current_app='core')

    def get_success_message(self, cleaned_data):
        return "Password reset."


class UserLogoutView(SiteRootView, TemplateView):
    template_name = 'bootstrap.html'

    def get(self, request, **kwargs):
        # if the user has no payment methods, redirect to the view where one can be created
        logout(self.request)
        return HttpResponseRedirect(reverse(viewname='location_list', current_app='core'))


class UserListView(SiteRootView, TemplateView):
    template_name = 'user/list.html'

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        users = User.objects.filter(is_active=True)
        context['users'] = users
        locationusers = []
        for u in users:
            u.locations_volatile = u.location_set.all()
            locationusers.append(u)
        context['locationusers'] = locationusers
        return context


from django.views.generic.edit import DeleteView
from django.core.urlresolvers import reverse_lazy


class UserDeactivateView(UserView, DeleteView):
    model = User
    template_name = 'user/deactivate.html'
    success_url = reverse_lazy('user_list')

    def delete(self, request, *args, **kwargs):
        """
        Replaces the delete() method, deactivates the user instead
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.is_active = False
        self.object.save()
        return HttpResponseRedirect(success_url)


class UserUpdateView(UserView, UpdateView):
    model = User
    template_name = 'base/form.html'

    def get_form_class(self):
        return cf.get_user_form_class(self.get_noun())

    def form_valid(self, form):
        user = self.get_noun()
        new_locations = form.cleaned_data['locations']
        current_locations = user.location_set.all()
        for l in current_locations:
            if l not in new_locations:
                l.members.remove(user)
        for l in new_locations:
            if l not in current_locations:
                l.members.add(user)
        return super(UserUpdateView, self).form_valid(form)


class LocationCreateView(SiteRootView, CreateView):
    model = cm.Location
    template_name = 'base/form.html'
    fields = '__all__'
    form_class = cf.LocationForm

    def get(self, request, *args, **kwargs):
        supes = super(LocationCreateView, self).get(request, *args, **kwargs)
        context = self.get_context_data(**kwargs)
        if self.request.is_ajax():
            data = json.dumps(context, default=decimal_default)
            out_kwargs = {'content_type': 'application/json'}
            return HttpResponse(data, **out_kwargs)

        return supes

    def get_success_url(self):
        action.send(self.request.user, verb='created location', action_object=self.object)
        return reverse(viewname='location_detail', args=(self.object.id,), current_app='core')


class LocationListView(SiteRootView, TemplateView):
    model = cm.Location
    template_name = 'overview/map.html'

    def get_context_data(self, **kwargs):
        context = super(LocationListView, self).get_context_data(**kwargs)

        output = []
        if self.request.user.is_staff:
            locations = cm.Location.objects.all().order_by('title')
        else:
            locations = self.request.user.location_set.all()

        if self.request.is_ajax():
            for l in locations:
                blob = {
                    'id': l.id,
                    'lattitude': l.position.latitude,
                    'longitude': l.position.longitude,
                    'title': l.title,
                    'indicator_ids': l.get_indicator_ids()
                }
                output.append(blob)
            context['locations'] = output
        else:
            context['locations'] = locations
            dimensions_qs = cm.Dimension.objects.select_related('parent') \
                .all().order_by('name')
            # '#' stands for no parent(root) in jstree plugin
            context['dimensions'] = map(lambda obj: dict(
                id=obj.id,
                parent=obj.parent.id if obj.parent else '#',
                text=obj.name,
                name=obj.name,   # alias
                icon='no-icon'  # class for avoiding icon
            ), dimensions_qs)
        context['stream'] = []
        # context['stream'] = am.Action.objects.all()[:40]
        return context

    def get(self, request, *args, **kwargs):
        if self.request.is_ajax():
            context = self.get_context_data(**kwargs)
            data = json.dumps(context, default=decimal_default)
            out_kwargs = {'content_type': 'application/json'}
            return HttpResponse(data, **out_kwargs)

        return super(LocationListView, self).get(request, *args, **kwargs)


class PlainLocationListView(SiteRootView, TemplateView):
    model = cm.Location
    template_name = 'overview/map.html'

    def get_context_data(self, **kwargs):
        context = super(PlainLocationListView, self).get_context_data(**kwargs)
        dimension_id = self.request.GET.get('dimension', None)
        output = []
        if self.request.user.is_staff:
            locations = cm.Location.objects.all()
        else:
            locations = self.request.user.location_set.all()

        if dimension_id:
            locations = locations.filter(dimensionpath__dimension=dimension_id)

        locations = locations.order_by('title')

        if self.request.is_ajax():
            for l in locations:
                blob = {
                    'id': l.id,
                    'lattitude': l.position.latitude if l.position else '0',
                    'longitude': l.position.longitude if l.position else '0',
                    'title': l.title,
                }
                output.append(blob)
            context['locations'] = output
        else:
            context['locations'] = locations
        context['stream'] = []
        # context['stream'] = am.Action.objects.all()[:40]
        return context

    def get(self, request, *args, **kwargs):
        if self.request.is_ajax():
            context = self.get_context_data(**kwargs)
            data = json.dumps(context, default=decimal_default)
            out_kwargs = {'content_type': 'application/json'}
            return HttpResponse(data, **out_kwargs)

        return super(PlainLocationListView, self).get(request, *args, **kwargs)


class LocationListStreamView(SiteRootView, ListView):
    model = am.Action
    template_name = 'overview/map.html'
    paginate_by = 10
    context_object_name = 'stream'
    queryset = am.Action.objects.all().select_related('actor', 'action_object', 'target')


class LocationView(NounView):
    def get_noun(self, **kwargs):
        return cm.Location.objects.get(id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(LocationView, self).get_context_data(**kwargs)
        context["background_image_url"] = self.get_noun().get_background_image_url()
        return context


class LocationUpdateView(LocationView, UpdateView):
    model = cm.Location
    template_name = 'base/form.html'
    success_url = '/'
    form_class = cf.LocationForm

    def get_success_url(self):
        action.send(self.request.user, verb='updated location', action_object=self.get_noun())
        return reverse(viewname='location_detail', args=(self.noun.id,), current_app='core')


class LocationDetailView(LocationView, TemplateView):
    model = cm.Location
    template_name = 'location/detail.html'

    def get_context_data(self, **kwargs):
        context = super(LocationDetailView, self).get_context_data(**kwargs)
        most_recent_image = self.noun.get_most_recent_image()
        if most_recent_image != None:
            context["most_recent_image_url"] = most_recent_image.get_file_url()
        # context["stream"] = self.noun.get_action_stream()[:40]
        context['stream'] = []
        return context


class LocationDetailStreamView(LocationView, ListView):
    model = am.Action
    template_name = 'location/detail.html'
    paginate_by = 10
    context_object_name = 'stream'

    def get_queryset(self, **kwargs):
        return self.noun.get_action_stream().select_related('actor', 'action_object', 'target')


class LocationPhotoListView(LocationView, ListView):
    template_name = 'location/photos.html'
    model = cm.Image
    paginate_by = 5

    def get_queryset(self):
        return self.get_noun().images.all()


class LocationIndicatorListlView(LocationView, TemplateView):
    model = cm.Location
    template_name = 'location/indicators.html'

    def get_context_data(self, **kwargs):
        context = super(LocationIndicatorListlView, self).get_context_data(**kwargs)
        # context['stream'] = self.noun.get_action_stream()[:40]
        context['stream'] = []
        context['indicators'] = self.noun.indicators.all().order_by('form_number', 'title')
        context['ILLEGAL_FIELD_LABELS'] = cm.ILLEGAL_FIELD_LABELS
        return context

    def get(self, request, *args, **kwargs):
        supes = super(LocationIndicatorListlView, self).get(request, *args, **kwargs)
        context = self.get_context_data(**kwargs)
        if self.request.is_ajax():
            data = json.dumps(context, default=decimal_default)
            out_kwargs = {'content_type': 'application/json'}
            return HttpResponse(data, **out_kwargs)
        return supes


try:
    import xlwt

    XLWT_INSTALLED = True
    XLWT_DATETIME_STYLE = xlwt.easyxf(num_format_str='MM/YYYY')
except ImportError:
    XLWT_INSTALLED = False
from io import BytesIO
from forms_builder.forms.utils import slugify

import re


class EntriesFilterView(SiteRootView, FormView):
    model = cm.Location
    template_name = 'base/form.html'
    form_class = cf.SavedFilterForm
    worksheet_names = {}

    def sanitize_worksheet_name(self, incoming):
        stripped_name = re.sub(r'[\W_]+', ' ', incoming[:31])
        if stripped_name in self.worksheet_names:
            self.worksheet_names[stripped_name] += 1;
            return stripped_name[:25] + " " + str(self.worksheet_names[stripped_name])
        else:
            self.worksheet_names[stripped_name] = 1
            return stripped_name

    def add_indicator_to_workbook(self, indicator, workbook, columns, saved_filter):
        sheet = workbook.add_sheet(self.sanitize_worksheet_name(indicator.get_title()))
        for c, col in enumerate(columns):
            sheet.write(0, c, col)
        for r, row in enumerate(indicator.get_filtered_entries(saved_filter, csv=True)):
            for c, item in enumerate(row):
                if isinstance(item, datetime.datetime):
                    item = item.replace(tzinfo=None)
                    sheet.write(r + 2, c, item, XLWT_DATETIME_STYLE)
                else:
                    sheet.write(r + 2, c, item)

        return workbook

    def form_valid(self, form):
        try:
            show_hidden_fields = form.cleaned_data['show_hidden']
        except Exception as e:
            show_hidden = False

        try:
            indicator = form.cleaned_data['indicator']
            columns = indicator.get_column_headers(show_hidden=show_hidden)
        except Exception as e:
            indicator = None

        if form.cleaned_data['export'] == True:
            response = HttpResponse(mimetype="application/vnd.ms-excel")
            fname = "%s-%s.xls" % ("QI Data Export", slugify(now().ctime()))
            attachment = "attachment; filename=%s" % fname
            response["Content-Disposition"] = attachment
            queue = BytesIO()
            workbook = xlwt.Workbook(encoding='utf8')
            if indicator == None:
                for i in cm.Indicator.objects.all().order_by("form_number"):
                    columns = i.get_column_headers(show_hidden=show_hidden)
                    workbook = self.add_indicator_to_workbook(i, workbook, columns,
                                                              form.cleaned_data)
            else:
                workbook = self.add_indicator_to_workbook(indicator, workbook, columns,
                                                          form.cleaned_data)
            workbook.save(queue)
            data = queue.getvalue()
            response.write(data)
            return response
        else:
            context = {
                "columns": columns,
                "entries": indicator.get_filtered_entries(form.cleaned_data, csv=False,
                                                          show_hidden=show_hidden),
                "available_verbs": self.noun.get_available_verbs(self.request.user),
                "filter": form.cleaned_data
            }
            return render_to_response('indicator/entries.html',
                                      context,
                                      context_instance=RequestContext(self.request))

    def get_form_kwargs(self):
        kwargs = super(EntriesFilterView, self).get_form_kwargs()
        kwargs['ajax_location'] = True
        return kwargs


class ScoresDetailView(SiteRootView, FormView):
    template_name = 'overview/scores.html'
    form_class = cf.DateForm

    def form_valid(self, form):
        the_date = form.cleaned_data['date']

        return HttpResponseRedirect(reverse(viewname='scores_date_list',
                                            kwargs={'month': the_date.month, 'year': the_date.year},
                                            current_app='core'))

    def get_context_data(self, **kwargs):
        context = super(ScoresDetailView, self).get_context_data(**kwargs)
        NOT_ASSIGNED_STRING = "N/A"
        NO_DATA_STRING = "N/D"
        try:
            month = int(self.kwargs['month'])
            year = int(self.kwargs['year'])
        except Exception as e:
            d = datetime.datetime.now()
            month = d.month
            year = d.year
        queryset = cm.Indicator.objects.all().order_by("form_number")
        columns = list(queryset.values_list('title', flat=True))
        indicator_ids = list(queryset.values_list('id', flat=True))
        # get all scores for this month
        rows = {}
        for l in cm.Location.objects.select_related('indicators').all():
            l_assignments = l.get_indicator_ids()
            # rows[l.id] = [l.title]+([NOT_ASSIGNED_STRING]*len(columns))
            l_cols = []
            for lc in indicator_ids:
                # if the column is assigned to this l, fill it with N/D
                if lc in l_assignments:
                    l_cols.append(NO_DATA_STRING)
                else:
                    # else fill it with N/A
                    l_cols.append(NOT_ASSIGNED_STRING)
            rows[l.id] = [l.title] + (l_cols)
        # add space to the begininbg of columns for the location names
        columns = ["Location"] + columns
        for s in cm.Score.objects.filter(month=str(month), year=year):
            # add the score object to the table if it exists
            indicator_index = indicator_ids.index(s.indicator.id) + 1
            if type(rows[s.location.id][indicator_index]) == unicode:
                rows[s.location.id][indicator_index] = s
            else:
                rows[s.location.id][indicator_index].merge(s)

        this_month = datetime.date(year, month, 1)

        # raise Exception(rows)
        context['this_month'] = this_month
        context['last_month'] = this_month - relativedelta(months=1)
        context['next_month'] = this_month + relativedelta(months=1)
        context['columns'] = columns
        context['entries'] = rows.values()
        return context


class LocationImageCreateView(LocationView, CreateView):
    model = cm.Image
    template_name = 'base/form.html'
    fields = ['original_file']

    def get_form(self, form_class):
        return cf.ImageForm(self.request.POST or None, self.request.FILES or None,
                            initial=self.get_initial())

    def form_valid(self, form):
        return super(LocationImageCreateView, self).form_valid(form)

    def get_success_url(self):
        self.noun.images.add(self.object)
        action.send(self.request.user, verb='uploaded image', action_object=self.object,
                    target=self.noun)
        return reverse(viewname='location_detail', args=(self.noun.id,), current_app='core')


class IndicatorCreateView(SiteRootView, CreateView):
    model = cm.Indicator
    template_name = 'base/form.html'
    form_class = cf.IndicatorForm

    def form_valid(self, form):
        new_form = fm.Form.objects.create(title=form.cleaned_data['title'][0:50])
        location_field = fm.Field.objects.create(form=new_form, field_type=1, label="Location",
                                                 visible=False, order=-2)
        location_field = fm.Field.objects.create(form=new_form, field_type=1, label="User",
                                                 visible=False, order=-1)
        location_field = fm.Field.objects.create(form=new_form, field_type=13, label="Score",
                                                 visible=False, order=0)
        form.instance.form = new_form
        self.instance = form.instance
        # action.send(self.request.user, verb='created', action_object=self.object, target=self.object)
        return super(IndicatorCreateView, self).form_valid(form)

    def get_success_url(self):
        action.send(self.request.user, verb='created indicator', action_object=self.instance)
        return reverse(viewname='field_create', args=(self.instance.id,), current_app='core')


class IndicatorView(NounView):
    def get_noun(self, **kwargs):
        return cm.Indicator.objects.get(id=self.kwargs['pk'])


class IndicatorUpdateView(IndicatorView, UpdateView):
    model = cm.Indicator
    template_name = 'base/form.html'
    success_url = '/'
    form_class = cf.IndicatorForm

    def get_success_url(self):
        self.get_noun().updated_at = datetime.datetime.now()
        action.send(self.request.user, verb='updated indicator', action_object=self.get_noun())
        return reverse(viewname='indicator_detail', args=(self.noun.id,), current_app='core')


class IndicatorDetailView(IndicatorView, TemplateView):
    model = cm.Indicator
    template_name = 'indicator/list.html'

    def get_context_data(self, **kwargs):
        context = super(IndicatorDetailView, self).get_context_data(**kwargs)
        context['ILLEGAL_FIELD_LABELS'] = cm.ILLEGAL_FIELD_LABELS
        # context['stream'] = self.noun.get_action_stream()[:40]
        context['stream'] = []
        context['ILLEGAL_FIELD_LABELS'] = cm.ILLEGAL_FIELD_LABELS
        return context

    def get_context_data(self, **kwargs):
        context = super(IndicatorDetailView, self).get_context_data(**kwargs)
        indicators = []
        indicators.append(self.noun.get_serialized())
        context['indicators'] = indicators
        context['ILLEGAL_FIELD_LABELS'] = cm.ILLEGAL_FIELD_LABELS

        return context

    def get(self, request, *args, **kwargs):
        supes = super(IndicatorDetailView, self).get(request, *args, **kwargs)
        context = self.get_context_data(**kwargs)
        if self.request.is_ajax():
            data = json.dumps(context, default=decimal_default)
            out_kwargs = {'content_type': 'application/json'}
            return HttpResponse(data, **out_kwargs)

        return supes


class IndicatorListView(SiteRootView, TemplateView):
    model = cm.Indicator
    template_name = 'indicator/list.html'

    def get_context_data(self, **kwargs):
        context = super(IndicatorListView, self).get_context_data(**kwargs)
        indicators = []
        for l in cm.Indicator.objects.all().order_by('form_number'):
            blob = l.get_serialized()
            indicators.append(blob)
        context['indicators'] = indicators
        context['ILLEGAL_FIELD_LABELS'] = cm.ILLEGAL_FIELD_LABELS
        return context

    def get(self, request, *args, **kwargs):
        supes = super(IndicatorListView, self).get(request, *args, **kwargs)
        context = self.get_context_data(**kwargs)
        if self.request.is_ajax():
            data = json.dumps(context, default=decimal_default)
            out_kwargs = {'content_type': 'application/json'}
            return HttpResponse(data, **out_kwargs)

        return supes


class FieldCreateView(IndicatorView, FormView):
    model = fm.Field
    template_name = 'base/form.html'

    def get_form(self, form_class):
        return cf.FieldForm(self.request.POST or None, self.request.FILES or None,
                            initial=self.get_initial())

    def form_valid(self, form):
        form.instance.form = self.noun.form
        form.instance.required = False
        self.object = form.instance.save()
        self.instance = form.instance
        return super(FieldCreateView, self).form_valid(form)

    def get_success_url(self):
        action.send(self.request.user, verb='created field', action_object=self.instance,
                    target=self.noun)
        return reverse(viewname='field_create', args=(self.noun.id,), current_app='core')

    def get_success_message(self, cleaned_data):
        return "Your field was created.  Make another new field or return to the indicator."


class FieldUpdateView(IndicatorView, UpdateView):
    model = fm.Field
    template_name = 'base/form.html'
    success_url = '/'

    def get_noun(self, **kwargs):
        return cm.Indicator.objects.get(id=self.kwargs['indicator_pk'])

    def get_object(self):
        output = get_object_or_404(fm.Field, id=self.kwargs["pk"])
        return output

    def get_form(self, form_class):
        return cf.FieldForm(self.request.POST or None, self.request.FILES or None,
                            initial=self.get_initial(), instance=self.get_object())

    def get_success_url(self):
        action.send(self.request.user, verb='updated field', action_object=self.get_object(),
                    target=self.noun)
        return reverse(viewname='indicator_detail', args=(self.noun.id,), current_app='core')


import json

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic.base import TemplateView

from forms_builder.forms.forms import FormForForm
from forms_builder.forms.models import Form

from forms_builder.forms.signals import form_invalid, form_valid

from django.contrib import messages


class IndicatorRecordCreateView(LocationView, TemplateView):
    template_name = "base/form.html"

    def get_noun(self, **kwargs):
        return cm.Location.objects.get(id=self.kwargs['location_pk'])

    def prep_form(self, form):
        # form.fields.__delitem__('location')
        # form.fields.__delitem__('user')
        return form

    def get_context_data(self, **kwargs):
        context = super(IndicatorRecordCreateView, self).get_context_data(**kwargs)
        published = Form.objects.published(for_user=self.request.user)
        indicator = get_object_or_404(cm.Indicator, id=kwargs["pk"])
        form = indicator.get_form()
        form = self.prep_form(form)
        context["form"] = form
        context["indicator"] = indicator
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        # throw an error if this user is not authorized
        # TODO: find a way to do this with carteblanche
        if (self.request.user.is_staff != True) and (
                    self.noun.members.filter(id=self.request.user.id).count() == 0):
            raise Exception(
                "You tried to create a record with a location you're not assigned to. You must be an Admin or a member of " + self.noun.title + " to create a new record.")
        indicator = get_object_or_404(cm.Indicator, id=kwargs["pk"])
        builder_form_object = indicator.get_builder_form_object()
        form = FormForForm(builder_form_object, RequestContext(request),
                           request.POST or None,
                           request.FILES or None)
        if not form.is_valid():
            form_invalid.send(sender=request, form=self.form_for_form)
        else:
            # Attachments read must occur before model save,
            # or seek() will fail on large uploads.
            attachments = []
            for f in form.files.values():
                f.seek(0)
                attachments.append((f.name, f.read()))
            indicator = get_object_or_404(cm.Indicator, id=kwargs["pk"])
            location = get_object_or_404(cm.Location, id=kwargs["location_pk"])
            form.cleaned_data["user"] = request.user.get_full_name()
            form.cleaned_data["location"] = location.__str__()
            entry = form.save()
            form_valid.send(sender=request, form=form, entry=entry)
            form = self.prep_form(form)
            score = indicator.score_entry(entry)
            context = self.get_context_data(**kwargs)
            if score >= indicator.passing_percentage:
                messages.success(request, 'Passing score of ' + str(score))
                action.send(self.request.user, verb='entered passing record',
                            action_object=context.get("indicator"), target=self.noun)
            else:
                messages.error(request, 'Not passing score of ' + str(score))
                action.send(self.request.user, verb='entered failing record',
                            action_object=context.get("indicator"), target=self.noun)
            return HttpResponseRedirect(reverse(viewname='indicator_record_create',
                                                args=(kwargs['location_pk'], kwargs['pk'],),
                                                current_app='core'))

        context = {"builder_form_object": builder_form_object, "form": form}
        return self.render_to_response(context)

    def render_to_response(self, context, **kwargs):
        if self.request.is_ajax():
            json_context = json.dumps({
                "errors": context["form_for_form"].errors,
                "form": context["form_for_form"].as_p(),
                "message": context["form"].response,
            })
            return HttpResponse(json_context, content_type="application/json")
        return super(IndicatorRecordCreateView, self).render_to_response(context, **kwargs)


form_detail = IndicatorRecordCreateView.as_view()

from forms_builder.forms.utils import now


class IndicatorRecordUploadView(LocationView, FormView):
    template_name = 'base/form.html'
    form_class = cf.JSONUploadForm
    success_url = '/'

    def get_noun(self, **kwargs):
        return cm.Location.objects.get(id=self.kwargs['location_pk'])

    def form_valid(self, form):
        try:
            # throw an error if this user is not authorized
            # TODO: find a way to do this with carteblanche
            if (self.request.user.is_staff != True) and (
                        self.noun.members.filter(id=self.request.user.id).count() == 0):
                raise Exception(
                    "You tried to synchronize a record with a location you're not assigned to. You must be an Admin or a member of " + self.noun.title + " to upload a new record.")
            json_string = form.cleaned_data['json']

            data = json.loads(json_string, parse_float=decimal.Decimal)
            day = 1
            try:
                day = int(data.get("day"))
            except Exception as e:
                pass
            new_entry_time = timezone.datetime(year=int(data.get("year")),
                                               month=int(data.get("month")), day=day)

            # create field entries for incoming data.  Don't save them until we're done
            fieldEntries = []
            for f in data.get("values"):
                field_id = f.get("field_id")
                new_value = f.get("value")
                if new_value == True:
                    new_value = u"True"
                elif new_value == False:
                    new_value = u"False"
                new_fieldEntry = fm.FieldEntry(value=new_value, field_id=field_id)
                fieldEntries.append(new_fieldEntry)
            if fieldEntries.__len__() > 0:
                # if there are entries, create a new record
                form_id = fm.Field.objects.get(id=field_id).form_id
                new_record = fm.FormEntry(entry_time=new_entry_time, form_id=form_id)
                new_record.save()
                for f in fieldEntries:
                    # connect the entries to the record
                    f.entry_id = new_record.id
                    f.save()
                # create entries for location and user data
                score = float(data.get("score"))
                builder_form = fm.Form.objects.get(id=form_id)
                new_locationEntry = fm.FieldEntry(value=self.get_noun().__str__(),
                                                  field_id=builder_form.fields.get(
                                                      label="Location").id, entry_id=new_record.id)
                new_locationEntry.save()
                new_userEntry = fm.FieldEntry(value=self.request.user.get_full_name(),
                                              field_id=builder_form.fields.get(label="User").id,
                                              entry_id=new_record.id)
                new_userEntry.save()
                new_scoreEntry = fm.FieldEntry(value=score,
                                               field_id=builder_form.fields.get(label="Score").id,
                                               entry_id=new_record.id)
                new_scoreEntry.save()

                # take the score from the json and create an action
                indicator = cm.Indicator.objects.get(form__id=form_id)
                if score == 100:
                    messages.success(self.request, 'Passing score of ' + str(score))
                    action.send(self.request.user, verb='PASS ' + str(score),
                                action_object=indicator, target=self.noun)
                else:
                    messages.error(self.request, 'Not passing score of ' + str(score))
                    action.send(self.request.user, verb='FAIL ' + str(score),
                                action_object=indicator, target=self.noun)
            context = {
                "status": "success",
                "record_id": new_record.id
            }
        except Exception as e:
            context = {
                "status": "failure",
                "error": e
            }
            messages.error(self.request, e)
        if self.request.is_ajax():
            data = json.dumps(context, default=decimal_default)
            out_kwargs = {'content_type': 'application/json'}
            return HttpResponse(data, **out_kwargs)
        else:

            return super(IndicatorRecordUploadView, self).form_valid(form)

    def get(self, request, *args, **kwargs):

        supes = super(IndicatorRecordUploadView, self).get(request, *args, **kwargs)
        context = self.get_context_data(**kwargs)
        if self.request.is_ajax():
            data = json.dumps(context, default=decimal_default)
            out_kwargs = {'content_type': 'application/json'}
            return HttpResponse(data, **out_kwargs)

        return supes


'''
incoming json looks like:
{
    "title":"blah blah blah",
    "scores":[
        {
            "percentage":100.00,
            "indicator_id":0,
            "location_id":0,
            "passing":true,
            "total_record_count":0,
            "passing_record_count":0
        }
    ]
}
'''


class LocationScoreUploadView(LocationView, FormView):
    template_name = 'base/form.html'
    form_class = cf.JSONUploadForm
    success_url = '/'

    def get_noun(self, **kwargs):
        return cm.Location.objects.get(id=self.kwargs['location_pk'])

    def form_valid(self, form):
        json_string = form.cleaned_data['json']

        try:
            data = json.loads(json_string, parse_float=decimal.Decimal)
            new_scores = []
            for s in data.get("scores"):
                # print type(s)
                # check to make sure the location matches

                if int(s.get("location_id")) != self.noun.id:
                    raise Exception("wrong score for this location")
                indicator_id = s.get("indicator_id")
                indicator = cm.Indicator.objects.get(id=indicator_id)
                # create but don't save untill all are created
                t = datetime.datetime(year=s.get("year"), month=s.get("month"), day=1)
                new_score = cm.Score(indicator=indicator, passing=s.get("passing"),
                                     entry_count=s.get("total_record_count"),
                                     passing_entry_count=s.get("passing_record_count"),
                                     month=str(s.get("month")), year=s.get("year"),
                                     score=s.get("percentage"), location=self.noun,
                                     user=self.request.user, datetime=t)
                new_scores.append(new_score)
                if settings.CACHING:
                    self.noun.invalidate_cached_series(indicator)
            # if nothing blew up, lets save these and invalidate the cached series data
            for s in new_scores:
                s.save()
            context = {
                "status": "success",
                "score_id": 0
            }
        except Exception as e:
            context = {
                "status": "failure",
                "error": e
            }
        if self.request.is_ajax():
            data = json.dumps(context, default=decimal_default)
            out_kwargs = {'content_type': 'application/json'}
            return HttpResponse(data, **out_kwargs)
        else:
            return super(LocationScoreUploadView, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        supes = super(LocationScoreUploadView, self).get(request, *args, **kwargs)
        context = self.get_context_data(**kwargs)
        if self.request.is_ajax():
            data = json.dumps(context, default=decimal_default)
            out_kwargs = {'content_type': 'application/json'}
            return HttpResponse(data, **out_kwargs)

        return supes


class LocationIndicatorVisualize(LocationView, TemplateView):
    template_name = "location/visualize.html"

    def get_noun(self, **kwargs):
        return cm.Location.objects.get(id=self.kwargs['location_pk'])

    def get(self, request, *args, **kwargs):
        supes = super(LocationIndicatorVisualize, self).get(request, *args, **kwargs)
        context = self.get_context_data(**kwargs)
        if self.request.is_ajax():
            t = datetime.datetime.now()
            year_ago = t - relativedelta(months=12)
            indicator = get_object_or_404(cm.Indicator, id=kwargs["pk"])
            # get all scores for this location/indicator from the last year
            scores = cm.Score.objects.filter(indicator__id=kwargs["pk"],
                                             location__id=kwargs['location_pk'],
                                             datetime__gte=year_ago).order_by('datetime')
            # iterate over scores averaging them if there are more than one per month

            data = []
            for s in scores:
                # multiplied by 1000 because apparently js doesn't understand utc
                blob = [time.mktime(s.datetime.timetuple()) * 1000, s.score]
                data.append(blob)
            output = {
                "name": self.noun.title,
                "id": self.noun.id,
                "data": data
            }
            context = self.get_context_data(**kwargs)
            context["series"] = [output]
            context["noun"] = {"title": self.noun.title}
            data = json.dumps(context, default=decimal_default)
            out_kwargs = {'content_type': 'application/json'}
            return HttpResponse(data, **out_kwargs)

        return supes


class LocationVisualize(LocationView, TemplateView):
    template_name = "location/visualize.html"

    def get(self, request, *args, **kwargs):
        if self.request.is_ajax():
            # store these results in a new series
            # add the series to
            context = self.get_context_data(**kwargs)
            context["series"] = self.noun.get_all_series()
            context["noun_title"] = self.noun.title
            context["location_id"] = self.noun.id
            context["noun"] = {"title": self.noun.title}
            data = json.dumps(context, default=decimal_default)
            out_kwargs = {'content_type': 'application/json'}
            return HttpResponse(data, **out_kwargs)

        return super(LocationVisualize, self).get(request, *args, **kwargs)


class LocationListVisualizeView(SiteRootView, TemplateView):
    template_name = "overview/visualize.html"

    def get_context_data(self, **kwargs):

        # Call the base implementation first to get a context
        context = super(LocationListVisualizeView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['indicators'] = cm.Indicator.objects.all().order_by('form_number')
        return context

    def get(self, request, *args, **kwargs):
        if self.request.is_ajax():
            all_series = []
            # for every location, get all_series
            for l in cm.Location.objects.filter(id=21).prefetch_related('indicators'):
                all_series.append(l.get_all_series())
            # store these results in a new series
            # add the series to
            context = self.get_context_data(**kwargs)
            context["series"] = all_series
            context["noun_title"] = "Overview"
            context["location_id"] = "-2"
            context["noun"] = {"title": "Overview"}
            data = json.dumps(context, default=decimal_default)
            out_kwargs = {'content_type': 'application/json'}
            return HttpResponse(data, **out_kwargs)

        dimension_qs = cm.Dimension.objects.all().order_by('name')
        kwargs['dimensions'] = dimension_qs

        return super(LocationListVisualizeView, self).get(request, *args, **kwargs)
