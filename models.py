

from django.db import models
from django.contrib.auth import models as auth_models
from django.contrib.auth.models import User, UserManager
from django.core.exceptions import ObjectDoesNotExist 
from django.utils.translation import ugettext as _
from locations.models import Location, LocationType
from django.utils.datastructures import SortedDict
from django.db.models import Sum

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from rapidsms.models import Contact, Connection




class HealthPost(Location, models.Model):
    
        TITLE = _(u"Health Posts")
        
       	class Meta:
            ordering = ["name"]
            verbose_name = "Location"

        def __unicode__(self):
		return u'%s %s' % (self.name, self.type.name)


	@classmethod
	def by_location(cls, location):
                try:
                        return cls.objects.get(location_ptr = location)
                except cls.DoesNotExist:
                        return None


        @classmethod
        def list_by_location(cls, location, type=None):
                if location == None:
                        health_posts = HealthPost.objects.all()
                else:
                        health_posts = []
                        for loc in location.descendants(include_self = True):
                                health_posts.append(cls.by_location(loc))
                        health_posts = filter(lambda hp: hp != None, health_posts)
                if type != None:
                        health_posts = filter(lambda hp: hp.type == type, health_posts)
                return health_posts

        @classmethod
        def get_late_healthposts(cls, current_period):
                entries = Entry.objects.all()
                current_entries = filter(lambda entries:
                                                  entries.report_period == current_period,
                                                  entries)
                submitted_healthposts=[]

                locations = HealthPost.objects.all()
                #filter locations which are health posts only
                health_posts = filter(lambda locations:
                                     locations.type.name.lower() == "health post",
                                     locations)
                
                #get health posts who has successfully sent their report.
                for entry in current_entries:
                        submitted_healthposts.append(entry.supply_place.location)
                
                #filter out the health posts who hasn't yet sent their report.  
                late_healthpost = filter(lambda health_posts: health_posts not in submitted_healthposts, health_posts)

                return late_healthpost

                

        @property
        def woreda(self):
                list = filter(lambda hp: hp.type.name.lower() == "woreda" , self.ancestors())
                
                if len(list) == 0:
                        return None
                else:
                        return list[0]
        @property
        def zone(self):
                list = filter(lambda hp: hp.type.name.lower() == "zone" , self.ancestors())
                
                if len(list) == 0:
                        return None
                else:
                        return list[0]

        @property
        def region(self):
                list = filter(lambda hp: hp.type.name.lower() == "region" , self.ancestors())
                
                if len(list) == 0:
                        return None
                else:
                        return list[0]
                        

        def _get_number_of_child_locations(self):
            if self.type.name.lower() != "health post":
                locs = self.children.all()
                return len(locs)

        def _get_parent_location(self):
            if self.type.name.lower() !=  "region":
                return self.parent

        def _get_parent_location_name(self):
            if self.type.name.lower() != "region":
                return self.parent.name

        def _get_location_type(self):
                return self.type.name

        def _get_descendant_locations(self):
            if self.type.name.lower() != "health post":
                locs = self.children.all()
                return locs

        def _get_reporters(self):
                reporters = []
                for reporter in RUTFReporter.objects.all():
                        if reporter.location.name == self.name:
                                reporters.append(reporter)
                return reporters

        def _get_reporters_name(self):
                reporters = self._get_reporters()
                reporters_name = ""
                for reporter in reporters:
                        reporters_name = reporters_name + unicode(reporter) + ", "
                
                return reporters_name
        

        number_of_child_location = property(_get_number_of_child_locations)

        parent_location = property(_get_parent_location)

        parent_location_name = property (_get_parent_location_name)

        location_type = property(_get_location_type)

        descendant_locations = property(_get_descendant_locations)

        reporters = property(_get_reporters)

        reporters_name = property(_get_reporters_name)

        @property
        def title(self):
                return self.TITLE
        

        @classmethod
        def table_columns(cls):
                columns = []
                columns.append({'name': 'Name',})
                columns.append({'name': 'Woreda',})
                columns.append({'name': 'Zone',})
                columns.append({'name': 'Reporters',})
                                
                sub_columns = None
                
                return columns, sub_columns
        

        @classmethod
        def aggregate_report(cls, scope = None,location_type = None,
                             location_name = None, startmonth_id = None,
                             endmonth_id = None, group = None):
                results = []

                # healthposts in the scope of the webuser
                locations = scope.health_posts()
                rutf_reporters = scope.rutf_reporters()

                # filter only health posts
                locations = filter(lambda locations:
                                   locations.type.name.lower() == "health post",
                                   locations)

                if location_type != "" and location_type != None and location_name != "" and location_name != None:
                        # Get all locations in the specified location
                        loc_selected = HealthPost.objects.filter(
                                name = location_name,
                                type__name = location_type)[0]
                        descendent_location = loc_selected.descendants(include_self = True)
                        descendent_location_code = [des_loc.code for des_loc in descendent_location]
                        locations = filter(lambda locations:
                                   locations.code in descendent_location_code, locations)
        
                if len(locations) == 0:
                        return results

                for location in locations:
                        result = SortedDict()
                        result["healthpost_id"] = location.id
                        result['name'] = "%s (%s)" % (location.name, location.code)
                        result['woreda'] = location.parent.name
                        result['zone'] = location.parent.parent.name
                        reporters = ["%s %s" % (rutf_reporter.first_name, rutf_reporter.last_name)
                                              for rutf_reporter in rutf_reporters
                                              if rutf_reporter.location == location]
                        
                        result['reporters'] = ", ".join(reporters)
                        results.append(result)
                
                return results


class Role(models.Model):
    """Basic representation of a role that someone can have.  For example,
       'supervisor' or 'data entry clerk'"""
    name = models.CharField(max_length=160)
    code = models.CharField(max_length=20, blank=True, null=True,\
        help_text="Abbreviation")
        
    def __unicode__(self):
        return self.name


class RUTFReporterConnection(Connection):
        
        class Meta:
		verbose_name = "RUTF Reporter Connection"
		

class RUTFReporter(Contact):

        user_name = models.CharField(unique = True, max_length=30, help_text = "username must be unique")
        first_name = models.CharField(max_length=30)
        last_name = models.CharField(max_length=30)
        grandfather_name = models.CharField(max_length=30, blank=True)

        location = models.ForeignKey(HealthPost, related_name="location", null=True, blank=True)
        role = models.ForeignKey(Role, related_name="roles", null=True, blank=True)
	email = models.EmailField(blank=True)
	is_active_reporter = models.BooleanField()
		
        TITLE = _(u"Rutf Reporter")
	
	class Meta:
		verbose_name = "Reporter"
		ordering = ['user_name']
	
	# the string version of RUTF reporter
	# now contains only their name i.e first_name last_name
	def __unicode__(self):
		return "%s %s" %\
			(self.first_name,
			self.last_name)
	
	def _get_latest_report(self):
		try:
			return Entry.objects.filter(rutf_reporter=self).order_by('-time')[0]
		
		except IndexError:
			return "N/A"

	latest_report = property(_get_latest_report)
	
	
	
	# 'summarize' the HEWs by
	# returning his full name and phone number
	def _get_details(self):
		
		return "%s" % (self)
	
	details = property(_get_details)

	#the place where the health officer is assigned
	#returns the location name and its type (i.e woreda, zone, or region)
	def _get_place_assigned(self):
                place_name = self.location.name or "unknown"
                place_type = self.location.type.name or "unknown"
                #return "%s %s" % (place_name, place_type)
                return self.location
        
        place_assigned = property(_get_place_assigned)

        def _get_phone_number(self):
                try:
                        return self.default_connection.identity
                except:
                        return None

        phone = property(_get_phone_number)


        def _has_phone(self):
                if self.phone != None:
                        return True
                else:
                        return False

        has_phone = property(_has_phone)

        
        @property
        def title(self):
                return self.TITLE

        @classmethod
        def table_columns(cls):
                columns = []
                columns.append({'name': 'User name',})
                columns.append({'name': 'Full Name',})
                columns.append({'name': 'Health Post',})
                columns.append({'name': 'Woreda',})
                columns.append({'name': 'Phone',})
                                
                sub_columns = None
                
                return columns, sub_columns


        @classmethod
        def aggregate_report(cls, scope = None,location_type = None,
                             location_name = None, startmonth_id = None,
                             endmonth_id = None, group = None):
                results = []

                # healthposts in the scope of the webuser
                rutf_reporters = scope.rutf_reporters()

                # deleted reporters
                deleted_reporters = DeletedItems.objects.filter(model_name = "RUTFReporter")
                deleted_reporters_id = [deleted_reporter.object_id for deleted_reporter in deleted_reporters]

                # filter reporter not deleted
##                rutf_reporters  = filter(lambda rutf_reporters:
##                                         rutf_reporters.id not in deleted_reporters_id, rutf_reporters)

                if location_type != "" and  location_type != None and location_name != "" and location_name != None:
                        # Get all locations in the specified location
                        loc_selected = HealthPost.objects.filter(
                                name = location_name,
                                type__name = location_type)[0]
                        descendent_location = loc_selected.descendants(include_self = True)
                        descendent_location_code = [des_loc.code for des_loc in descendent_location]
                        rutf_reporters = filter(lambda rutf_reporters:
                                   rutf_reporters.location.code in descendent_location_code, rutf_reporters)
        
                
                #keys = ['name', 'code', 'unit']

                if len(rutf_reporters) == 0:
                        return results

                for rutf_reporter in rutf_reporters:
                        result = SortedDict()
                        result['reporter_id'] = rutf_reporter.id
                        result['username'] = rutf_reporter.user_name
                        result['first_name'] = "%s %s" % (rutf_reporter.first_name, rutf_reporter.last_name)
                        result['health_post'] = rutf_reporter.location.name
                        result['woreda'] = rutf_reporter.location.parent.name
                        result['phone'] = rutf_reporter.phone
                        results.append(result)
                        
                return results



class LateHealthPost(models.Model):
        """ Model used to store late health post id and reporter's id
        with extended number of days. This model is updated every reporting period"""
        
        location = models.ForeignKey(HealthPost, help_text = "Name of late Healthposts")
        rutf_reporter = models.ForeignKey(RUTFReporter, help_text = "Name of active reporter in healthposts")
        accept_late_report = models.BooleanField(help_text = "Is the health post allowed to report late (for the current period)?")
        extended_days = models.PositiveIntegerField(default= 3, help_text="Number of days extended. (By default, it is set to 3 days)")

        class Meta:
                unique_together = ("location", "rutf_reporter")
        


class Supply(models.Model):
        UNIT_CHOICES = (
                ('CTN', 'Cartons'),
                ('PL', 'pallets'),
                ('TM', 'Tons (metric)'),
                ('KG', 'Kilograms'),
                ('BX', 'Boxes'),
                ('TB', 'Tiny boxes'),
                ('BL', 'Bales'),
                ('LT', 'Liters'),
                ('CN', 'Containers'),
                ('DS', 'Doses'),
                ('VI', 'Vials'),
                ('SA', 'Sachets'),
                ('BG', 'Bags'),
                ('BT', 'Bottles'),
                ('UK', 'Unknown'),
            )
	name = models.CharField(max_length=100, unique=True)
	code = models.CharField(max_length=20, unique=True)
	unit = models.CharField(max_length=3, verbose_name="Measurement Unit", choices=UNIT_CHOICES)

        TITLE = _(u"Supplies")
	
	class Meta:
		verbose_name_plural="Supplies"

	def __unicode__(self):
		return self.name

	
	def guess(self):
		return [self.name, self.code]

	@property
        def title(self):
                return self.TITLE


	@classmethod
        def table_columns(cls):
                columns = []
                columns.append({'name': 'Supply Name',})
                columns.append({'name': 'Supply Code',})
                columns.append({'name': 'Unit',})
                
                
                sub_columns = None
                
                return columns, sub_columns
        
        @classmethod
        def aggregate_report(cls, scope = None,location_type = None,
                             location_name = None, startmonth_id = None,
                             endmonth_id = None, group = None):
                results = []
                
                # supplies in all the places
                supplies = Supply.objects.all()

                keys = ['name', 'code', 'unit']
##                for key in keys:
##                        result[key] = None

                if len(supplies) == 0:
                        return results

                for supply in supplies:
                        result = SortedDict()
                        result['name'] = supply.name
                        result['code'] = supply.code
                        result['unit'] = supply.unit
                        results.append(result)
                        
                return results


	

class SupplyPlace(models.Model):
	supply = models.ForeignKey(Supply)
	location = models.ForeignKey(HealthPost, verbose_name="Health Post", blank=True, null=True, help_text="Name of Location")
	quantity = models.PositiveIntegerField(blank=True, null=True, help_text="Balance at Location")
	
	def __unicode__(self):
		return "%s" %\
		(self.place)

	class Meta:
		verbose_name_plural="Supplies per Location"
	
	def _get_place(self):
		if self.location: return self.location
		
	place = property(_get_place)
	
	def _get_type(self):
		if self.location: return self.location.type.name
		
	type = property(_get_type)
		
	
class Alert(models.Model):
	rutf_reporter = models.ForeignKey(RUTFReporter)
	time = models.DateTimeField(auto_now_add=True)
	notice = models.CharField(blank=True, max_length=160, help_text="Alert from Health extension worker")
	resolved = models.BooleanField(help_text="Has the alert been attended to?")
	
        TITLE = _(u"Alert")

	def __unicode__(self):
		return "%s by %s" %\
		(self.time.strftime("%d/%m/%y"), self.rutf_reporter)
	
	class Meta:
		verbose_name_plural="Alert Message"
		ordering = ['-time']

	@property
        def title(self):
                return self.TITLE


	@classmethod
        def table_columns(cls):
                columns = []
                columns.append({'name': 'Alert',})
                columns.append({'name': 'Time',})
                columns.append({'name': 'Is Resolved',})
                columns.append({'name': 'Reported By',})
                
                sub_columns = None
                
                return columns, sub_columns

        @classmethod
        def aggregate_report(cls, scope = None,location_type = None,
                             location_name = None, startmonth_id = None,
                             endmonth_id = None, group = None):
                results = []

                # alerts in the scope of the webuser
                alerts = scope.alerts()

                if location_type != "" and location_name != "":
                        # Get all locations in the specified location
                        loc_selected = HealthPost.objects.filter(
                                name = location_name,
                                type__name = location_type)[0]
                        descendent_location = loc_selected.descendants(include_self = True)
                        descendent_location_code = [des_loc.code for des_loc in descendent_location]
                        alerts = filter(lambda alerts:
                                   alerts.rutf_reporter.location.code in descendent_location_code, alerts)

                # if time rage is given, filter the alerts based on the range
##                if startmonth_id != "":
##                        startmonth_start_date = ReportPeriod.objects.filter(id = startmonth_id)[0].start_date
##                        if endmonth_id != "":
##                                #endmonth_start_date = ReportPeriod.objects.filter(id = endmonth_id)[0].start_date
##                                endmonth_end_date = ReportPeriod.objects.filter(id = endmonth_id)[0].end_date
##                                alerts = filter(lambda alerts:
##                                                startmonth_start_date <= alerts.time and
##                                                alerts.time <= endmonth_end_date , alerts)
##                        else:
##                                startmonth_end_date = ReportPeriod.objects.filter(id = startmonth_id)[0].end_date
##                                alerts = filter(lambda alerts:
##                                                startmonth_start_date <= alerts.time and
##                                                alerts.time <= startmonth_end_date , alerts)
                             
        
                
                #keys = ['name', 'code', 'unit']

                if len(alerts) == 0:
                        return results

                for alert in alerts:
                        result = SortedDict()
                        result['Alert'] = alert.notice
                        result['Time'] = alert.time
                        result['Is_Resolved'] = alert.resolved
                        result['Reported_by'] = "%s %s" % (alert.rutf_reporter.first_name,
                                                           alert.rutf_reporter.last_name) 
                        results.append(result)
                        
                return results


##class ReportPeriod(models.Model):
##        start_date = models.DateTimeField()
##        end_date = models.DateTimeField()
##
##        class Meta:
##                unique_together = ("start_date", "end_date")
##                get_latest_by = "end_date"
##                ordering = ["-end_date"]
##
##        def __unicode__(self):
##                return "%s to %s" % (self.start_date,self.end_date)

class ReportPeriod(models.Model):
        month = models.CharField(max_length = 20, help_text="Report period month")
        year = models.PositiveIntegerField(help_text="Report period year")
        start_date = models.DateTimeField(help_text="Report period start date in GC")
        end_date = models.DateTimeField(help_text="Report period end date in GC")
        reporting_start_date = models.DateTimeField(help_text="Reporting period start date in GC")
        reporting_end_date = models.DateTimeField(help_text="Reporting period end date in GC (Deadline)")

        class Meta:
                unique_together = ("month", "year")
                get_latest_by = "month"
                

        def __unicode__(self):
                return "%s-%s" % (self.month,self.year)


class Entry(models.Model):
	rutf_reporter = models.ForeignKey(RUTFReporter, help_text="Health Extension Worker / Health officer")
	supply_place = models.ForeignKey(SupplyPlace, verbose_name="Place", help_text="The Health post/Woreda/Zone which this report was sent from")
	quantity = models.PositiveIntegerField("Quantity", null=True)
	consumption = models.PositiveIntegerField("Consumption", null=True)
	balance = models.PositiveIntegerField("Balance", null=True)
        time = models.DateTimeField(auto_now_add=True)
        report_period = models.ForeignKey(ReportPeriod, verbose_name="Period", help_text="The period in which the data is reported")
        receipt = models.CharField(max_length=20, help_text="Receipt number of the Report")
        late = models.BooleanField(help_text="Has the report made late?")
        confirmed_by_woreda = models.BooleanField(verbose_name = "Conf. By Woreda",help_text="Confirmed by Woreda")
        confirmed_by_zone = models.BooleanField(verbose_name = "Conf. By Zone", help_text="Confirmed by Zone")
        confirmed_by_region = models.BooleanField(verbose_name = "Conf. By Region", help_text="Confirmed by Region") 



        TITLE = _(u"Reported Entries")
        
	def __unicode__(self):
		return "%s on %s" %\
		(self.supply_place, self.time.strftime("%d/%m/%y"))
	
	class Meta:
		verbose_name_plural="Entries"
		ordering = ['-time']


	def _get_receipt(self):
                return _(u"%(health_post)sM%(month)s/%(reportid)s") % \
                             {'health_post': self.supply_place.location.id, 'month': self.report_period.id,
                              'reportid': self.id}

                                 
        new_receipt = property(_get_receipt)

        @property
        def title(self):
                return self.TITLE
        

        @classmethod
        def table_columns(cls):
                columns = []
                columns.append({'name': 'Health Post',})
                #columns.append({'name': 'Item',})
                columns.append({'name': 'Quantity Received',})
                columns.append({'name': 'Consumption',})
                columns.append({'name': 'Balance',})
                columns.append({'name': 'Reported By',})
                columns.append({'name': 'Month',})

                sub_columns = None
                
                return columns, sub_columns

        @classmethod
        def table_aggregate_columns(cls):
                columns = []
                columns.append({'name': 'Total Quantity',})
                columns.append({'name': 'Total Consumption',})
                columns.append({'name': 'Total Balance',})
                
                sub_columns = None
                
                return columns, sub_columns


        @classmethod
        def aggregate_report(cls, scope = None,location_type = None,
                             location_name = None, startmonth_id = None,
                             endmonth_id = None, group = None):
                
                
                # entries in the scope of the webuser
                entries = scope.entries()
                webuser_location = scope.location
                
                                                
                # filter only confirmed entries
                if webuser_location.type.name.lower() == "zone":
                        entries = filter(lambda entries: entries.confirmed_by_woreda == True, entries)
                elif webuser_location.type.name.lower() == "region":
                        entries = filter(lambda entries: entries.confirmed_by_zone == True, entries)
                elif webuser_location.type.name.lower() == "federal":
                        entries = filter(lambda entries: entries.confirmed_by_region == True, entries)
                elif webuser_location.type.name.lower() == "woreda":
                        # show all the entries
                        entries = entries
                else:
                        entries = filter(lambda entries: entries.confirmed_by_region == True, entries)

                if location_type != "" and location_name != "":
                        # Get all locations in the specified location
                        loc_selected = HealthPost.objects.filter(
                                name = location_name,
                                type__name = location_type)[0]
                                   
                        descendent_location = loc_selected.descendants(include_self = True)
                        descendent_location_code = [des_loc.code for des_loc in descendent_location]
                        entries = filter(lambda entries:
                                   entries.supply_place.location.code in descendent_location_code, entries)
                                      

                # if time range is given, filter the entries based on the range

##                if startmonth_id != "" and startmonth_id is not None:
##                        # Get the period range from the given date from ReportPeriod
##                        startmonth_start_date = ReportPeriod.objects.filter(id = startmonth_id)[0].start_date
##                        if endmonth_id != "":
##                                #endmonth_start_date = ReportPeriod.objects.filter(id = endmonth_id)[0].start_date
##                                endmonth_end_date = ReportPeriod.objects.filter(id = endmonth_id)[0].end_date
##                                entries = filter(lambda entries: startmonth_start_date <= entries.time and
##                                                 entries.time <= endmonth_end_date, entries)
##                        else:
##                                startmonth_end_date = ReportPeriod.objects.filter(id = startmonth_id)[0].end_date
##                                entries = filter(lambda entries: startmonth_start_date <= entries.time and
##                                                 entries.time <= startmonth_end_date , entries)


                if startmonth_id != "" and startmonth_id is not None:
                        if endmonth_id != "" and endmonth_id is not None:
                                entries = filter(lambda entries: int(startmonth_id) <= entries.report_period.id and
                                                 entries.report_period.id <= int(endmonth_id), entries)
                        else:
                                entries = filter(lambda entries: entries.report_period.id == int(startmonth_id), entries)


                                
                                        
                # if group by option is given, it will aggregate the report

                if group is not None:
                        results = SortedDict()
                        # locations in the specified group location
                        locations = HealthPost.list_by_location(group)
                        
                        for key in ['quantity', 'consumption', 'balance']:
                                results[key] = None

                        # First filter the entries based on the above parameter and scope
                        # if type cast is possible, we can simply cast the entries list to
                        # queryset to apply aggregate function
                        
                        entry_ids = [entry.id for entry in entries]
                        entries_filtered = Entry.objects.filter(id__in = entry_ids,
                                                                supply_place__location__in = locations)

                        agg_queryset = entries_filtered.aggregate(quantity = Sum('quantity'),
                                                   consumption = Sum('consumption'),
                                                   balance = Sum('balance'))
                                            
                        for key, value in agg_queryset.items():
                                results[key] = value
                                results['complete'] = True

                        return results

                else:
                        results = []
                        if len(entries) == 0:
                                return results

                        for entry in entries:
                                result = SortedDict()
                                result['supply_place'] = entry.supply_place
                                #result['item_name'] = entry.supply_place.supply.name
                                result['quantity'] = entry.quantity
                                result['consumption'] = entry.consumption
                                result['balance'] = entry.balance
                                result['Reported_by'] = "%s %s" % (entry.rutf_reporter.first_name,
                                                                   entry.rutf_reporter.last_name)
                                result['month'] = "%s %s" % (entry.report_period.month,entry.report_period.year)
                                
                                # it lists entries. each entry is complete  
                                #result['complete'] = True
                                results.append(result)
                        
                        return results

        


class WebUser(User):
        ''' Extra fields for web users '''

        TITLE = _(u"Web Users")

        class Meta:
                pass

        def __unicode__(self):
                return unicode(self.user_ptr)

        # Use UserManager to get the create_user method, etc.
        objects = UserManager()
##      location = models.ForeignKey(Location, blank=True, null=True)
    
        location = models.ForeignKey(HealthPost)

        def health_posts(self):
                '''Return the health posts within the location of the WebUser'''
                if self.location == None:
                        return HealthPost.objects.all()
                else:
                        return HealthPost.list_by_location(self.location)

        def scope_string(self):
                if self.location == None:
                        return 'All'
                else:
                        return self.location.name

        def rutf_reporters(self):

                """ Return the rutf reporters within
                the health posts of the related reporter"""

                health_posts = self.health_posts()
                rutf_reporters = []
                for rutf_reporter in RUTFReporter.objects.filter(role__code='hew'):
                        if HealthPost.by_location(rutf_reporter.location) in health_posts:
                                rutf_reporters.append(rutf_reporter)
                        return rutf_reporters

        @classmethod
        def by_user(cls, user):
                try:
                        return cls.objects.get(user_ptr=user)
                except cls.DoesNotExist:
                        new_user = cls(user_ptr=user)
                        new_user.save_base(raw=True)
                        return new_user

        @property
        def title(self):
                return self.TITLE
                
        
        @classmethod
        def table_columns(cls):
                columns = []
                columns.append({'name': 'Name',})
                columns.append({'name': 'Father Name',})
                columns.append({'name': 'User Name',})
                columns.append({'name': 'Place Assigned',})
                
                sub_columns = None
                
                return columns, sub_columns

        @classmethod
        def aggregate_report(cls, scope = None,location_type = None,
                             location_name = None, startmonth_id = None,
                             endmonth_id = None, group = None):
                results = []

                # healthposts in the scope of the webuser
                web_users = scope.web_user()

                if location_type != "" and location_name != "":
                        # Get all locations in the specified location
                        loc_selected = HealthPost.objects.filter(
                                name = location_name,
                                type__name = location_type)[0]
                        descendent_location = loc_selected.descendants(include_self = True)
                        descendent_location_code = [des_loc.code for des_loc in descendent_location]
                        web_users = filter(lambda web_users:
                                   web_users.location.code in descendent_location_code, web_users)
        
                
                #keys = ['name', 'code', 'unit']

                if len(web_users) == 0:
                        return results

                for web_user in web_users:
                        result = SortedDict()
                        result['first_name'] = web_user.first_name
                        result['last_name'] = web_user.last_name
                        result['phone'] = web_user.username
                        result['location'] = web_user.location.name 
                        results.append(result)
                        
                return results
        

class DeletedItems(models.Model):
        model_name = models.CharField(max_length=20, help_text="Name of model")
        content_type = models.ForeignKey(ContentType)
        object_id = models.PositiveIntegerField()

        content_object = generic.GenericForeignKey('content_type', 'object_id')


        class Meta:
                pass
                #unique_together = ("model_name", "item_id")


##        def _get_item_object(self):
##                model = models.get_model("rutfet", self.model_name)
##                try:
##                        item_object = model.objects.get(id = self.object_id)
##                        return item_object
##                except Exception, e:
##                        print e
##                        return None
##
##        item_object = property(_get_item_object)

        
