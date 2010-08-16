

from django.db import models
from django.contrib.auth import models as auth_models
from django.contrib.auth.models import User, UserManager
from django.core.exceptions import ObjectDoesNotExist 
from django.utils.translation import ugettext as _
from reporters.models import Reporter
from locations.models import Location, LocationType


class RUTFReporter(Reporter):
        grandfather_name = models.CharField(max_length=30, blank=True)
	phone = models.CharField(max_length=15, blank=True, help_text="e.g., +251912555555")
	email = models.EmailField(blank=True)
		
	
	class Meta:
		verbose_name = "RUTF Reporter"
		ordering = ['first_name']
	
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
		phone_number = self.phone or "unknown"
		return "%s (%s)" % (self, phone_number)
	
	details = property(_get_details)

	#the place where the health officer is assigned
	#returns the location name and its type (i.e woreda, zone, or region)
	def _get_place_assigned(self):
                place_name = self.location.name or "unknown"
                place_type = self.location.type.name or "unknown"
                return "%s %s" % (place_name, place_type)
        
        place_assigned = property(_get_place_assigned)




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
	unit = models.CharField(max_length=3, choices=UNIT_CHOICES)
	
	class Meta:
		verbose_name_plural="Supplies"

	def __unicode__(self):
		return self.name

	
	def guess(self):
		return [self.name, self.code]


	
class HealthPost(Location, models.Model):
    
       	class Meta:
            ordering = ["name"]      

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

        @property
        def woreda(self):
                list = filter(lambda hp: hp.type.name.lower == "woreda", self.ancestors())
                
                if len(list) == 0:
                        return None
                else:
                        return list[0]

        def zone(self):
                list = filter(lambda hp: hp.type.name.lower == "zone", self.ancestors())
                
                if len(list) == 0:
                        return None
                else:
                        return list[0]

        def region(self):
                list = filter(lambda hp: hp.type.name.lower == "region", self.ancestors())
                
                if len(list) == 0:
                        return None
                else:
                        return list[0]
                        

        def _get_number_of_child_locations(self):
            if self.type.name.lower() != "otp_site":
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

        number_of_child_location = property(_get_number_of_child_locations)

        parent_location = property(_get_parent_location)

        parent_location_name = property (_get_parent_location_name)

        location_type = property(_get_location_type)


class SupplyPlace(models.Model):
	supply = models.ForeignKey(Supply)
	location = models.ForeignKey(HealthPost, verbose_name="Health Post", blank=True, null=True, help_text="Name of Location")
	quantity = models.PositiveIntegerField(blank=True, null=True, help_text="Balance at Location")
	
	def __unicode__(self):
		return "%s at %s (%s)" %\
		(self.supply.name, self.place, self.type)

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
	
	def __unicode__(self):
		return "%s by %s" %\
		(self.time.strftime("%d/%m/%y"), self.rutf_reporter)


class ReportPeriod(models.Model):
        start_date = models.DateTimeField()
        end_date = models.DateTimeField()

        class Meta:
                unique_together = ("start_date", "end_date")
                get_latest_by = "end_date"
                ordering = ["-end_date"]

        def __unicode__(self):
                return "%s to %s" % (self.start_date,self.end_date)


class Entry(models.Model):
	rutf_reporter = models.ForeignKey(RUTFReporter, help_text="Health Extension Worker / Health officer")
	supply_place = models.ForeignKey(SupplyPlace, verbose_name="Place", help_text="The Health post/Woreda/Zone which this report was sent from")
	quantity = models.PositiveIntegerField("Received Quantity", null=True)
	consumption = models.PositiveIntegerField("Consumption", null=True)
	balance = models.PositiveIntegerField("Current Stock Balance", null=True)
        time = models.DateTimeField(auto_now_add=True)
        report_period = models.ForeignKey(ReportPeriod, verbose_name="Period", help_text="The period in which the data is reported")
        
	def __unicode__(self):
		return "%s on %s" %\
		(self.supply_place, self.time.strftime("%d/%m/%y"))
	
	class Meta:
		verbose_name_plural="Entries"


	def _get_receipt(self):
                return _(u"%(health_post)sW%(week)s/%(reportid)s") % \
                             {'health_post': self.supply_place.location.id, 'week': self.report_period.id,
                              'reportid': self.id}

                                 
        receipt = property(_get_receipt)


class WebUser(User):
    ''' Extra fields for web users '''

    class Meta:
        pass

    def __unicode__(self):
        return unicode(self.user_ptr)

    # Use UserManager to get the create_user method, etc.
    objects = UserManager()

    location = models.ForeignKey(Location, blank=True, null=True)

    def health_posts(self):

        """
        Return the health posts within the location of the WebUser
        """
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

        """
        Return the rutf reporters within
        the health posts of the related reporter
        """

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


