#!/usr/bin/env python
# vim: noet

from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from models import *



class RUTFReporterAdmin(admin.ModelAdmin):
	list_display = ('first_name', 'last_name', 'alias', 'phone', 'email', 'latest_report')
	search_fields = ('first_name', 'last_name', 'alias')

class EntryAdmin(admin.ModelAdmin):
	list_display = ('supply_place', 'quantity','consumption', 'balance', 'time', 'rutf_reporter')
	list_filter = ['time']
	date_hierarchy = 'time'
	ordering = ['time']	
	search_fields = ('supply_place__location__name', 'supply_place__area__name', 'monitor__first_name', 'monitor__last_name', 'monitor__alias')


	
class HealthPostAdmin(admin.ModelAdmin):
	list_display = ('name', 'code','location_type', 'number_of_child_location','parent_location_name')
	list_filter = ['parent','type']
	search_fields = ('name', 'code','parent_location_name')


class AlertAdmin(admin.ModelAdmin):
	list_display = ('rutf_reporter', 'notice', 'time', 'resolved')
	list_filter = ['resolved', 'time']
	date_hierarchy = 'time'
	ordering = ['resolved']


class SupplyAdmin(admin.ModelAdmin):
	list_display = ('name', 'code', 'unit')

class SupplyPlaceAdmin(admin.ModelAdmin):
	list_display = ('location', 'supply', 'quantity')
	radio_fields = {'supply' : admin.HORIZONTAL}


# add our models to the django admin
admin.site.register(RUTFReporter, RUTFReporterAdmin)
admin.site.register(Supply, SupplyAdmin)
admin.site.register(HealthPost, HealthPostAdmin)
admin.site.register(SupplyPlace, SupplyPlaceAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(WebUser)

