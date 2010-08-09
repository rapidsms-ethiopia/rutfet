
from django.db import models
from django.contrib.auth import models as auth_models
from django.core.exceptions import ObjectDoesNotExist 
##from utils import otp_code, woreda_code
from reporters.models import Reporter
from locations.models import Location


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
                place_name = "unknown"
                place_type = "unknown"
                return "%s %s" % (place_name, place_type)
        
        place_assigned = property(_get_place_assigned)




class Supply(models.Model):
        UNIT_CHOICES = (
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
	
	def _get_number_of_reports(self):
		return len(Report.objects.filter(supply=self.id))

	number_of_reports = property(_get_number_of_reports)


class Location(Location, models.Model):
    
        def save(self):
		# if this Woreda or OTP_site does not already
		# have a code, assign a new one

		# For woreda
		if self.type.name.lower() == "woreda":
                    if(self.code == ""):
                            c = woreda_code()
                            self.code = c
                # For otp_site            
                if self.type.name.lower() == "otp_site":
                    if(self.code == ""):
                            c = otp_code()
                            self.code = c
		
		# invoke parent to save data
		models.Model.save(self)

	class Meta:
            ordering = ["name"]      #you can include "Region" for Zone location type

        def __unicode__(self):
		#return "%s (%s)" % (self.name, self.code)
		return self.name

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

        number_of_child_location = property(_get_number_of_child_locations)

        parent_location = property(_get_parent_location)

        parent_location_name = property (_get_parent_location_name)


class SupplyPlace(models.Model):
	supply = models.ForeignKey(Supply)
	location = models.ForeignKey(Location, verbose_name="OTP", blank=True, null=True, help_text="Name of OTP")
	#woreda = models.ForeignKey(Area, verbose_name="Woreda", blank=True, null=True, help_text="Name of Woreda")
	#zone = models.ForeignKey(Area, verbose_name="Woreda", blank=True, null=True, help_text="Name of Woreda")
	quantity = models.PositiveIntegerField(blank=True, null=True, help_text="Balance at OTP")
	
	def __unicode__(self):
		return "%s at %s (%s)" %\
		(self.supply.name, self.place, self.type)

	class Meta:
		verbose_name_plural="Supplies per OTP or Woreda"
	
	def _get_place(self):
		if self.location: return self.location
##		elif self.woreda:   return self.area
##		elif self.zone: return self.zone
		else:             return "Unknown"
	place = property(_get_place)
	
	def _get_type(self):
		if self.location: return "OTP"
##		elif self.area:   return "Woreda"
##		elif self.zone: return self.zone
		else:             return "Unknown"
	type = property(_get_type)
		
	def _get_area(self):
		if self.location: return self.location.area
##		elif self.area:   return self.area
##		elif self.zone: return self.zone
		else:             return "Unknown"
	woreda = property(_get_area)


class Alert(models.Model):
	rutf_reporter = models.ForeignKey(RUTFReporter)
	time = models.DateTimeField(auto_now_add=True)
	notice = models.CharField(blank=True, max_length=160, help_text="Alert from Health extension worker")
	resolved = models.BooleanField(help_text="Has the alert been attended to?")
	
	def __unicode__(self):
		return "%s by %s" %\
		(self.time.strftime("%d/%m/%y"), self.reporter)


##class Report(models.Model):
##	supply = models.ForeignKey(Supply)
##	begin_date = models.DateField()
##	end_date = models.DateField()
##	supply_place = models.ForeignKey(SupplyPlace)
##
##	def __unicode__(self):
##		return "%s report" % self.supply.name
##	
##	def _get_latest_entry(self):
##		try:
##			e = Entry.objects.order_by('-time')[0]
##		except:
##			e = "No Entries"
##		return e
##	
##	def _get_number_of_entries(self):
##		return len(Entry.objects.filter(time__gte=self.begin_date).exclude(time__gte=self.end_date))
##
##	number_of_entries = property(_get_number_of_entries)
##	latest_entry = property(_get_latest_entry)
	

class Entry(models.Model):
	rutf_reporter = models.ForeignKey(RUTFReporter, help_text="Health Extension Worker / Health officer")
	supply_place = models.ForeignKey(SupplyPlace, verbose_name="Place", help_text="The OTP or Woreda which this report was sent from")
	quantity = models.PositiveIntegerField("Received Quantity", null=True)
	consumption = models.PositiveIntegerField("Consumption", null=True)
	balance = models.PositiveIntegerField("Current Stock Balance", null=True)
        entry_time = models.DateTimeField(auto_now_add=True)
        
	def __unicode__(self):
		return "%s on %s" %\
		(self.supply_place, self.time.strftime("%d/%m/%y"))
	
	class Meta:
		verbose_name_plural="Entries"



