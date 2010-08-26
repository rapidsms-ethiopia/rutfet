#!/usr/bin/env python
# vim: noet

from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from models import *
from forms import *



class RUTFReporterAdmin(admin.ModelAdmin):
	list_display = ('first_name', 'last_name', 'alias', 'phone', 'email', 'latest_report')
	search_fields = ('^first_name', '^last_name', '^alias')
	fields = ('alias', 'first_name', 'last_name', 'grandfather_name', 'location', 'phone', 'email', 'role', 'groups', 'language', 'registered_self')
	#fields = ('first_name', 'last_name', 'grandfather_name','location')
	#filter_horizontal = ('groups',)
        
        #form = RUTFReporterForm
        
	def queryset(self, request):
                qs = super(RUTFReporterAdmin, self).queryset(request)
                webuser = WebUser.by_user(request.user)
                webuser_location = webuser.location
                child_locations = webuser_location.descendants(include_self = True)
                return qs.filter(location__in = child_locations)

   


class EntryAdmin(admin.ModelAdmin):
	list_display = ('supply_place', 'quantity','consumption', 'balance', 'time', 'rutf_reporter')
	list_filter = ['time']
	date_hierarchy = 'time'
	ordering = ['time']	
	search_fields = ('supply_place__location__name', 'supply_place__area__name', 'monitor__first_name', 'monitor__last_name', 'monitor__alias')

        def queryset(self, request):
                qs = super(EntryAdmin, self).queryset(request)
                webuser = WebUser.by_user(request.user)
                webuser_location = webuser.location
                child_locations = webuser_location.descendants(include_self = True)
                #Select supply places from the same location
                supply_places = SupplyPlace.objects.filter(location__in = child_locations)
                return qs.filter(supply_place__in = supply_places)

	
class HealthPostAdmin(admin.ModelAdmin):
	list_display = ('name', 'code','location_type', 'number_of_child_location','parent_location_name')
	list_filter = ['parent','type']
	search_fields = ('name', 'code','parent_location_name')
        
        form = HealthPostForm
        def queryset(self, request):
                qs = super(HealthPostAdmin, self).queryset(request)
                webuser = WebUser.by_user(request.user)
                webuser_location = webuser.location
                child_locations = webuser_location.descendants(include_self = True)
                child_locations_code = [child_location.code for child_location in child_locations]
                               
                return qs.filter(code__in = child_locations_code)

                
        
class AlertAdmin(admin.ModelAdmin):
	list_display = ('rutf_reporter', 'notice', 'time', 'resolved')
	list_filter = ['resolved', 'time']
	date_hierarchy = 'time'
	ordering = ['resolved']

	def queryset(self, request):
                qs = super(AlertAdmin, self).queryset(request)
                webuser = WebUser.by_user(request.user)
                webuser_location = webuser.location
                child_locations = webuser_location.descendants(include_self = True)
                #Select RUTF Reporters from the same location as the web-user
                rutf_reporters = RUTFReporter.objects.filter(location__in = child_locations)
                               
                return qs.filter(rutf_reporter__in = rutf_reporters)



class SupplyAdmin(admin.ModelAdmin):
	list_display = ('name', 'code', 'unit')

class SupplyPlaceAdmin(admin.ModelAdmin):
	list_display = ('location', 'supply', 'quantity')
	radio_fields = {'supply' : admin.HORIZONTAL}

	def queryset(self, request):
                qs = super(AlertAdmin, self).queryset(request)
                webuser = WebUser.by_user(request.user)
                webuser_location = webuser.location
                child_locations = webuser_location.descendants(include_self = True)
                                               
                return qs.filter(location__in = child_locations)


# add our models to the django admin
admin.site.register(RUTFReporter, RUTFReporterAdmin)
admin.site.register(Supply, SupplyAdmin)
admin.site.register(HealthPost, HealthPostAdmin)
admin.site.register(SupplyPlace, SupplyPlaceAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(WebUser)

