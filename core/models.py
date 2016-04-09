from django.contrib.auth.models import User
from django.db import models

# from carteblanche.django.mixins import DjangoVerb
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.contenttypes.models import ContentType
import actstream
from django.db.models import Q
import uuid
import os
from geoposition.fields import GeopositionField
from core.verbs import *
import forms_builder.forms.models as fm
import forms_builder.forms.fields as ff
from django.core.cache import get_cache
import datetime
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
from django.utils import timezone
from django.conf import settings

from dimension.models import Dimension

loc_cache = get_cache('default')
loc_cache.set("panda", "bear")

ILLEGAL_FIELD_LABELS = ['User', 'Location', 'Score']

ALLOWED_FIELD_TYPES = [ff.TEXT, ff.TEXTAREA, ff.CHECKBOX]
FIELD_TYPE_NAMES = ["TEXT", "TEXTAREA", "CHECKBOX"]

DEFAULT_PASSING = 85.00

MONTH_CHOICES = (
    ('1', 'Jan'),
    ('2', 'Feb'),
    ('3', 'Mar'),
    ('4', 'Apr'),
    ('5', 'May'),
    ('6', 'Jun'),
    ('7', 'Jul'),
    ('8', 'Aug'),
    ('9', 'Sep'),
    ('10', 'Oct'),
    ('11', 'Nov'),
    ('12', 'Dec'),
)


def get_file_path(instance, filename):
    blocks = filename.split('.')
    ext = blocks[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    instance.name = blocks[0]
    return os.path.join('uploads/', filename)


@python_2_unicode_compatible
class Auditable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    changed_by = models.ForeignKey(User, null=True, blank=True,
                                   related_name="%(app_label)s_%(class)s_related")

    def __str__(self):
        return "auditable string goes here"

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user_setter(self, value):
        self.changed_by = value

    def get_action_stream(self):
        stream = actstream.models.Action.objects.filter(self.get_action_stream_query()).order_by(
            '-timestamp')
        return stream

    def get_action_stream_query(self):
        post_type = ContentType.objects.get_for_model(self)
        query = Q(target_object_id=self.id, target_content_type=post_type)
        return query

    def get_class_name(self):
        return self.__class__.__name__

    #    def get_background_image_url(self):
    #        return None

    class Meta:
        abstract = True


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


class Image(Auditable, Noun):
    original_file = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    internal_file = models.ImageField(upload_to='/', null=True, blank=True)

    def __unicode__(self):
        return "Image"
        url = self.get_file_url()
        if url == None:
            return "No File"
        else:
            return url

    def get_file_url(self):
        if self.original_file != None:
            return self.original_file.url.replace("https", "http")
        else:
            return "pandas"

    def get_pandas(self):
        return "NOT PANDAS"


class Location(Auditable, Noun):
    title = models.TextField()
    position = GeopositionField()
    dimension = models.ForeignKey(Dimension, null=True, verbose_name='Dimension',
                                  related_name='locations')
    indicators = models.ManyToManyField('Indicator', null=True, blank=True)
    members = models.ManyToManyField(User, null=True, blank=True)
    images = models.ManyToManyField(Image, null=True, blank=True)
    dimension_tags = models.ManyToManyField(Dimension,
                                            null=True,
                                            through='DimensionPath')
    verb_classes = [LocationDetailVerb, LocationDetailStreamVerb, LocationVisualizeVerb,
                    LocationUpdateVerb, LocationPhotoListVerb, LocationIndicatorListVerb,
                    LocationImageCreateVerb]

    def __unicode__(self):
        return self.title

    def update_dimension_tags(self, dimension):
        path = dimension.get_path()
        path.append(dimension.id)
        self.dimension_tags.clear()
        for index, dimension_id in enumerate(list(set(path))):
            DimensionPath.objects.create(location=self, dimension_id=dimension_id,
                                         level=(index + 1))

    def get_absolute_url(self):
        return reverse(viewname='location_detail', args=[self.id], current_app=APPNAME)

    def get_members(self):
        return self.members.all()

    def get_indicators(self):
        return self.indicators.all()

    def get_indicator_ids(self):
        return list(self.indicators.all().values_list('id', flat=True))

    def get_most_recent_image(self):
        try:
            return self.images.all().order_by('-created_at')[:1][0]
        except Exception as e:
            return None

    def get_month_score_key(self, month, year):
        series_key = "location_scores_" + str(self.id) + "_" + str(month) + "_" + str(year)
        # print series_key
        return series_key

    def get_background_image_url(self):
        try:
            return self.get_most_recent_image().get_file_url()
        except AttributeError as e:
            return None

    def get_scores(self):
        return cm.Score.objects.filter(location=self)

    def get_month_scores(self, month, year):
        return self.get_scores().filter(month=str(month), year=year)

    def get_series_key(self, indicator):
        series_key = "location_" + str(self.id) + "_indicator_" + str(indicator.id)
        # print series_key
        return series_key

    def get_all_series_key(self):
        series_key = "location_" + str(self.id) + "_all_indicators"
        # print series_key
        return series_key

    def get_series(self, indicator):
        passing_percent = {}
        value = loc_cache.set("rambo", "junior")
        if settings.CACHING:
            key = self.get_series_key(indicator)
            value = loc_cache.get(key)
        else:
            value = None
        if value != None:
            # print key+" Found, Returning from cache"
            return value
        else:
            # print "Missing, Querying Fresh"
            t = timezone.now()
            year_ago = t - relativedelta(months=12)
            # get all scores for this location/indicator from the last year
            # scores = Score.objects.filter(indicator=indicator,location=self, datetime__gte=year_ago, entry_count__gt=0).order_by('datetime')
            scores = self.score_set.filter(indicator=indicator, datetime__gte=year_ago,
                                           entry_count__gt=0).order_by('datetime')
            # scores = self.score_set.all()
            # iterate over scores averaging them if there are more than one per month
            merged_scores = OrderedDict()
            for s in scores:
                # s.datetime.day = 1
                if merged_scores.has_key(s.get_month_year_key()):
                    merged_scores[s.get_month_year_key()].merge(s)

                else:
                    merged_scores[s.get_month_year_key()] = s
            scores = merged_scores.values()
            data = []
            for s in scores:
                # multiplied by 1000 because apparently js doesn't understand utc
                blob = [s.datetime.strftime("%Y-%m-1 00:00:00"), s.score, s.passing,
                        s.datetime.strftime("%B")]
                data.append(blob)
            i_series = {
                "name": indicator.get_long_name(),
                "id": indicator.id,
                "data": data
            }
            # print "Saving "+key+"to cache"
            if settings.CACHING:
                loc_cache.set(key, i_series, None)

        return i_series

    def invalidate_cached_series(self, indicator):
        # invalidate the cache of this indicator series
        loc_cache.delete(self.get_series_key(indicator))
        # invalidate the location's all_seriese cached data
        loc_cache.delete(self.get_all_series_key())

    def get_all_series(self):
        if settings.CACHING:
            loc_cache = get_cache('default')
            key = self.get_all_series_key()
            value = loc_cache.get(key)
        else:
            value = None
        if value != None:
            # print "Found, Returning from cache"
            return value
        else:
            # print "Missing, Querying Fresh"
            def percentage(part, whole, decimals=2):
                return 100 * float(part) / float(whole)

            t = datetime.datetime.now()
            year_ago = t - relativedelta(months=12)
            indicators = self.get_indicators().order_by('form_number')
            indicators_count = indicators.count()
            if indicators_count == 0:
                return []
            series = []
            for i in indicators:
                series.append(self.get_series(i))
                counts = OrderedDict()
            for s in series:
                # iterate over each blob
                for d in s["data"]:
                    # print s
                    # print d
                    # if counts doesn't contain the timestamp key, add it
                    class datum(object):
                        timestamp = None
                        is_passing = None

                    d_timestamp = d[0]
                    d_passing = d[2]
                    if not counts.has_key(d_timestamp):
                        # store 1 there if the score is passing
                        if d_passing == True:
                            print "store 1 there if the score is passing"
                            counts[d_timestamp] = [1, 1]
                        # store 0 if it's failing
                        elif d_passing == False:
                            print "store 0 if it's failing"
                            counts[d_timestamp] = [0, 1]
                    # otherwise update
                    else:
                        print "otherwise update"
                        # add 1 if passing
                        if d_passing == True:
                            print "add 1 if passing"
                            counts[d_timestamp][0] = counts[d_timestamp][0] + 1
                            counts[d_timestamp][1] = counts[d_timestamp][1] + 1
                        else:
                            print "add 1 to total count only if failing"
                            counts[d_timestamp][1] = counts[d_timestamp][1] + 1
                            # do nothing if failing
                # iterate over counts, calculating counts[n]/indicators.count
                print counts
            print "final count:"
            print counts
            # raise Exception(counts)
            goals_met_data = [[k, percentage(v[0], v[1]), percentage(v[0], v[1]) >= DEFAULT_PASSING,
                               DEFAULT_PASSING] for k, v in counts.items()]
            goals_met_data = sorted(goals_met_data, key=lambda k: k[0])
            goals_met_series = {
                "name": "PERCENT OF GOALS MET",
                "data": goals_met_data,
                "lineWidth": 6,
                "dashStyle": 'longdash',
                "id": "p"
            }
            series.append(goals_met_series)

        if settings.CACHING:
            loc_cache.set(key, series, None)
        return series


def update_cached(self, force_check_all):
    # get all scores for this location created since last update
    last_update = t - relativedelta(days=1)
    scores = cm.Score.objects.filter(location=self, datetime__gte=year_ago).order_by('datetime')
    invalidated_keys = []
    # invalidate all_series data
    for s in scores:
        score_location = s.location
        score_indicator = s.indicator
        score_location.invalidate_cached_series(s.indicator)
        # getting the series data automatically caches it if there is no cached data already
        score_location.get_series(score_indicator)
    # set this location's last_cached datetime to now
    self.last_cached = datetime.datetime.now()


from forms_builder.forms.forms import FormForForm
from django.template.context import Context
from django_remote_forms.forms import RemoteForm


class Indicator(Auditable, Noun):
    title = models.TextField()
    form = models.ForeignKey(fm.Form, unique=True, null=True, blank=True)
    form_number = models.IntegerField(null=True, blank=True)
    passing_percentage = models.FloatField(default=85)
    maximum_monthly_records = models.IntegerField(default=20)
    verb_classes = [IndicatorListVerb, IndicatorDetailVerb, IndicatorUpdateVerb, FieldCreateVerb,
                    FieldUpdateVerb]

    def __unicode__(self):
        return self.get_title()

    def get_form_number_string(self):
        if self.form_number != None:
            return "#" + str(self.form_number)
        else:
            return ""

    def get_long_name(self):
        return self.get_form_number_string() + " " + self.title + " [GOAL: " + str(
            self.passing_percentage) + "%]"

    def get_absolute_url(self):
        return reverse(viewname='indicator_detail', args=[self.id], current_app=APPNAME)

    def get_builder_form_object(self):
        return self.form

    def get_form(self):
        c = Context()
        return FormForForm(self.get_builder_form_object(), c)

    def get_bool_field_ids(self):
        return self.get_builder_form_object().fields.filter(field_type=4).values_list('id',
                                                                                      flat=True)

    def score_entry(self, entry):
        bool_field_ids = self.get_bool_field_ids()
        passing = []
        for f in entry.fields.all():
            if f.field_id in bool_field_ids:
                if f.value == u'True':
                    passing.append(f)
        return float(len(passing)) / float(len(bool_field_ids)) * 100

    def get_serialized_builder_form(self):
        remote_form = RemoteForm(self.get_form())
        remote_form_dict = remote_form.as_dict()
        return remote_form_dict

    def get_fields(self, show_hidden=None):
        field_queryset = self.form.fields.all().order_by("order")
        if show_hidden != True:
            field_queryset = field_queryset.exclude(visible=False)
        return field_queryset

    def get_serialized_fields(self, show_hidden=None):
        fields = []
        field_queryset = self.get_fields(show_hidden=show_hidden)
        for f in field_queryset:
            if f.field_type in ALLOWED_FIELD_TYPES:
                blob = {
                    "id": f.id,
                    "field_type": FIELD_TYPE_NAMES[ALLOWED_FIELD_TYPES.index(f.field_type)],
                    "help_text": f.help_text,
                    "label": f.label,
                    "order": f.order,
                    "visible": f.visible
                }
                fields.append(blob)
        return fields

    def get_title(self):
        if self.form_number != None:
            return "#" + str(self.form_number) + " " + self.title
        else:
            return self.title

    def get_serialized(self):
        blob = {
            'id': self.id,
            'title': self.get_title(),
            'passing_percentage': self.passing_percentage,
            'maximum_monthly_records': self.maximum_monthly_records,
            'url': self.get_absolute_url(),
            'fields': self.get_serialized_fields()
        }

        return blob

    def get_column_headers(self, show_hidden=None):
        return ["Date"] + list(
            self.get_fields(show_hidden=show_hidden).order_by("order").values_list('label',
                                                                                   flat=True))

    def get_filtered_entries(self, savedFilter, csv=False, show_hidden=None):
        # Store the index of each field against its ID for building each
        # entry row with columns in the correct order. Also store the IDs of
        # fields with a type of FileField or Date-like for special handling of
        # their values.
        user_field_id = self.form.fields.get(label="User").id
        # print "user_field_id: "+str(user_field_id)
        input_user_values = []
        for u in savedFilter['input_user']:
            input_user_values.append(u.get_full_name())
        # print "input_user_values: "+str(input_user_values)

        location_field_id = self.form.fields.get(label="Location").id
        # print "location_field_id: "+str(location_field_id)
        location_values = list(savedFilter['locations'].values_list('title', flat=True))
        if len(location_values) == 0:
            location_values = Location.objects.all().values_list('title', flat=True)
        # print "location_values: "+str(location_values)

        field_indexes = {}
        for field in self.get_fields(show_hidden=show_hidden).order_by("order"):
            field_indexes[field.id] = len(field_indexes)
        # get all field entries from the given form
        field_entries = fm.FieldEntry.objects.filter(entry__form=self.form
                                                     ).order_by("-entry__id").select_related(
            "entry")
        try:
            # if a date range is specified filter out any entries outside of the range
            if savedFilter['start_date']:
                field_entries = field_entries.filter(
                    entry__entry_time__gte=savedFilter['start_date'])
        except AttributeError as e:
            raise Exception(e)
        try:
            # if a date range is specified filter out any entries outside of the range
            if savedFilter['end_date']:
                field_entries = field_entries.filter(entry__entry_time__lte=savedFilter['end_date'])
        except AttributeError as e:
            raise Exception(e)
        try:
            # if a date range is specified filter out any entries outside of the range
            if savedFilter['start_date'] and savedFilter['end_date']:
                field_entries = field_entries.filter(
                    entry__entry_time__range=(savedFilter['start_date'], savedFilter['end_date']))
        except AttributeError as e:
            raise Exception(e)
        # Loop through each field value ordered by entry, building up each
        # entry as a row. Use the ``valid_row`` flag for marking a row as
        # invalid if it fails one of the filtering criteria specified.
        current_entry = None
        current_row = None
        valid_row = True
        num_columns = len(field_indexes)
        '''
        output = {}
        for field_entry in field_entries:
            #if output doesn't contain a blob for the formentry, create one with enough columns 
            #find the appropriate blob and 
        '''

        for field_entry in field_entries:
            ##print field_entry.id
            ##print "field_entry.field_id: "+str(field_entry.field_id)
            field_value = field_entry.value or "N/D"
            if field_value == "True":
                field_value = "Yes"
            elif field_value == "False":
                field_value = "No"
            ##print field_value
            if field_entry.entry_id != current_entry:
                # New entry, write out the current row and start a new one.
                if valid_row and current_row is not None:
                    if not csv:
                        current_row.insert(0, current_entry)
                    yield current_row
                current_entry = field_entry.entry_id
                current_row = [""] * num_columns
                valid_row = True
                current_row = [field_entry.entry.entry_time] + current_row
            # print "field_entry.field_id: "+str(field_entry.field_id)
            if len(input_user_values) > 0:
                if field_entry.field_id == user_field_id:
                    if not field_entry.value in input_user_values:
                        valid_row = False

            if field_entry.field_id == location_field_id:
                if not unicode(field_entry.value) in location_values:
                    valid_row = False

            # Only use values for fields that were selected.
            try:
                # shift over 1 to make room for the date column
                current_row[field_indexes[field_entry.field_id] + 1] = field_value
                # print current_row
            except KeyError:
                # print "KeyError current_row["+str(field_indexes)+"["+str(field_entry.id)+"]]"+fm.Field.objects.get(id=field_entry.field_id).label
                pass

        # Output the final row.
        if valid_row and current_row is not None:
            if not csv:
                current_row.insert(0, current_entry)
            yield current_row


class Score(Auditable):
    user = models.ForeignKey(User)
    indicator = models.ForeignKey(Indicator)
    location = models.ForeignKey(Location)
    score = models.FloatField(default=85)
    passing = models.BooleanField()
    entry_count = models.IntegerField()
    passing_entry_count = models.IntegerField()
    month = models.CharField(max_length=2, choices=MONTH_CHOICES)
    year = models.IntegerField()
    datetime = models.DateTimeField()

    def __unicode__(self):
        return str(self.score) + " : " + str(self.datetime)

    def get_status(self):
        if self.passing == True:
            return "passing"
        else:
            return "failing"

    def get_month_year_key(self):
        return str(self.datetime.month) + "_" + str(self.datetime.year)

    def is_passing(self):
        if self.score >= self.indicator.passing_percentage:
            return True
        else:
            return False

    def calculate_score(self):
        try:
            self.score = float(self.passing_entry_count) / self.entry_count * 100
            self.passing = self.is_passing()
            if (self.score == 100) and (self.is_passing() == False):
                raise Exception("uh oh")
        except ZeroDivisionError as e:
            pass

    def merge(self, incoming_score):
        if incoming_score.indicator != self.indicator:
            raise Exception("Can't Merge Scores From Different Indicators")
        if incoming_score.indicator != self.indicator:
            raise Exception("Can't Merge Scores From Different Locations")
        self.entry_count += incoming_score.entry_count
        self.passing_entry_count += incoming_score.passing_entry_count
        self.calculate_score()


class DimensionPath(models.Model):
    location = models.ForeignKey(Location)
    dimension = models.ForeignKey(Dimension)
    level = models.PositiveIntegerField()

    def __unicode__(self):
        return u'{}: {}::{}'.format(self.level, self.dimension.name, self.location.name)
