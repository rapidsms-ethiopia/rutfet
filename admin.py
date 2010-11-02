#!/usr/bin/env python
# vim: noet

from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from models import *
from forms import *

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
import django.forms as forms
from datetime import datetime, timedelta
from utils import send_text_message

from rapidsms.contrib.scheduler.models import EventSchedule

from django.utils.translation import ugettext, ugettext_lazy as _

from django.contrib.admin.actions import delete_selected
#delete_selected.short_description = u'How\'s this for a name?'



class RUTFReporterConnectionInline(admin.TabularInline):
    model = RUTFReporterConnection
    extra = 1

##class RUTFReporterAdmin(admin.ModelAdmin):
##    inlines = [RUTFReporterConnectionInline,]

class RUTFReporterAdmin(admin.ModelAdmin):
        inlines = [RUTFReporterConnectionInline,]
	list_display = ('first_name', 'last_name', 'user_name', 'location', 'phone', 'is_active_reporter')
	list_filter = ['location', 'is_active_reporter',]
	search_fields = ('^first_name', '^last_name', '^user_name')
	fields = ('user_name', 'first_name', 'last_name', 'grandfather_name', 'location', 'email', 'role', 'language', 'is_active_reporter')
	actions = ['set_reporter_active', 'set_reporter_inactive', 'delete_reporter','delete_selected']

	#fields = ('first_name', 'last_name', 'grandfather_name','location')
	#filter_horizontal = ('groups',)
        
        #form = RUTFReporterForm
        
	def queryset(self, request):
                qs = super(RUTFReporterAdmin, self).queryset(request)
                webuser = WebUser.by_user(request.user)
                webuser_location = webuser.location
                
                # deleted reporters
                deleted_reporters = DeletedItems.objects.filter(model_name = "RUTFReporter")
                deleted_reporters_id = [deleted_reporter.object_id for deleted_reporter in deleted_reporters]

                
                if webuser_location is not None:
                    child_locations = webuser_location.descendants(include_self = True)
                    qs = qs.filter(location__in = child_locations)
                    # exclude deleted items
                    qs = qs.exclude(id__in = deleted_reporters_id)
                                       
                    return qs
                
                else:
                    return qs


        def set_reporter_active(self, request, queryset):
                ''' Filter selected reporters who have phone number,
                and set them as active reporters. '''

                selected_reporters = len(queryset)
                reporters_with_phone = queryset.filter(connection__identity__isnull = False)
                rows_updated = 0
                for reporter in reporters_with_phone:
                    place_assigned = reporter.place_assigned
                    hp_reporters = place_assigned.reporters
                    for hp_reporter in hp_reporters:
                        if hp_reporter == reporter:
                            reporter.is_active_reporter = True
                            reporter.save()
                            rows_updated += 1
                        else:
                            hp_reporter.is_active_reporter = False
                            hp_reporter.save()
                            
                rows_not_updated = selected_reporters - rows_updated
                
                # Display message to the user
                if rows_updated ==1:
                    updated_no = "1 reporter was"
                    success_message = "%s sucessfully set to active reporter" % updated_no
                elif rows_updated > 1:
                    updated_no = "%s reporters were" % rows_updated
                    success_message = "%s sucessfully set to active reporter" % updated_no

                if rows_not_updated == 1:
                    not_updated_no = "1 reporter was"
                    failure_message = "%s not set to active reporter.(No phone number registered)" % not_updated_no
                elif rows_not_updated > 1:
                    not_updated_no = "%s reporters were" % rows_updated
                    failure_message = "%s not set to active reporter.(May be no phone number registered)" % not_updated_no


                if rows_updated != 0 and rows_not_updated != 0:
                    self.message_user(request, "%s. But %s" % (success_message,failure_message))
                else:
                    if rows_updated != 0:
                        self.message_user(request, "%s" % success_message)
                    elif rows_not_updated != 0:
                        self.message_user(request, "%s" % failure_message)

        def set_reporter_inactive(self, request, queryset):
                rows_updated = queryset.update(is_active_reporter = False)
                # Display message to the user
                if rows_updated ==1:
                    message_no = "1 reporter was"
                elif rows_updated > 1:
                    message_no = "%s reporters were" % rows_updated

                self.message_user(request, "%s sucessfully set to inactive reporter" % message_no)


        def delete_reporter(self , request, queryset):
                model_name = "RUTFReporter"
                for reporter in queryset:
                    DeletedItems.objects.create(model_name = model_name,
                                                object_id = reporter.id,
                                                content_object = reporter)
                                        


class EntryAdmin(admin.ModelAdmin):
	list_display = ('supply_place', 'quantity','consumption', 'balance', 'time', 'rutf_reporter',
                        'confirmed_by_woreda','confirmed_by_zone','confirmed_by_region')
	#list_display = ('supply_place', 'time', 'rutf_reporter')
	list_filter = ['report_period','confirmed_by_woreda', 'confirmed_by_zone' , 'confirmed_by_region']
	date_hierarchy = 'time'
	ordering = ['time']	
	search_fields = ('supply_place__location__name', 'supply_place__area__name', 'monitor__first_name', 'monitor__last_name', 'monitor__alias')
	readonly_fields = ['confirmed_by_woreda','confirmed_by_zone', 'confirmed_by_region']
        actions = ['confirm_report','delete_selected']
        
        def queryset(self, request):
                qs = super(EntryAdmin, self).queryset(request)
                webuser = WebUser.by_user(request.user)
                webuser_location = webuser.location

                if webuser_location is not None:
                    child_locations = webuser_location.descendants(include_self = True)
                    #Select supply places from the same location
                    supply_places = SupplyPlace.objects.filter(location__in = child_locations)
                    # And also filter reports which are confirmed
                    cofirmed_queryset = None
                    if webuser_location.type.name == "woreda":
                        cofirmed_queryset = qs.filter(supply_place__in = supply_places)
                    elif webuser_location.type.name == "zone":
                        cofirmed_queryset = qs.filter(supply_place__in = supply_places, confirmed_by_woreda = True)
                    elif webuser_location.type.name == "region":
                        cofirmed_queryset = qs.filter(supply_place__in = supply_places, confirmed_by_zone = True)
                    elif webuser_location.type.name == "federal":
                        cofirmed_queryset = qs.filter(supply_place__in = supply_places, confirmed_by_region = True)
                    else:
                        cofirmed_queryset = qs.filter(supply_place__in = supply_places,
                                                      confirmed_by_region = True)
                    return cofirmed_queryset
                else:
                    return qs

        class ConfirmationForm(forms.Form):
                _selected_action = forms.CharField(widget = forms.MultipleHiddenInput)

        

        def confirm_report(self, request, queryset):
                form = None
                
                if 'apply' in request.POST:
                    form = self.ConfirmationForm(request.POST)

                    if form.is_valid():
                        webuser = WebUser.by_user(request.user)
                        webuser_location = webuser.location
                        if webuser_location.type.name == "woreda":
                            # perform woreda level confirmation
                            rows_updated = queryset.update(confirmed_by_woreda = True)
                        elif webuser_location.type.name == "zone":
                            # perform zone level confirmation
                            rows_updated = queryset.update(confirmed_by_zone = True)
                        elif webuser_location.type.name == "region":
                            # perform region level confirmation
                            rows_updated = queryset.update(confirmed_by_region = True)

                        # Display message to the user
                        if rows_updated ==1:
                            message_no = "1 entry was"
                        elif rows_updated > 1:
                            message_no = "%s entries were" % rows_updated

                        self.message_user(request, "%s sucessfully confirmed" % message_no)

                        return HttpResponseRedirect(request.get_full_path())
                    
                elif 'cancel' in request.POST:
                    self.message_user(request, 'Confirmation is Canceled.')
                    return HttpResponseRedirect(request.get_full_path())

                    
                if not form:
                    form = self.ConfirmationForm(
                        initial = {'_selected_action':request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

                return render_to_response('admin/confirmation.html',
                                          {'entries':queryset,
                                           'confirmation_form':form,
                                           'path':request.get_full_path()},
                                          context_instance=RequestContext(request))
            
#confirm_report.short_description = "Confirm Entries"
                    
                
        
	
class HealthPostAdmin(admin.ModelAdmin):
	list_display = ('name', 'code','location_type','parent_location_name')
	list_filter = ['type']
	search_fields = ('name', 'code')
        
        #form = HealthPostForm
        def queryset(self, request):
                qs = super(HealthPostAdmin, self).queryset(request)
                webuser = WebUser.by_user(request.user)
                webuser_location = webuser.location
                if webuser_location is not None:
                    child_locations = webuser_location.descendants(include_self = True)
                    child_locations_code = [child_location.code for child_location in child_locations]
                    return qs.filter(code__in = child_locations_code)
                else:
                    return qs


class LateHealthPostAdmin(admin.ModelAdmin):
        list_display = ('location', 'rutf_reporter','accept_late_report', 'extended_days')
	list_filter = ['accept_late_report']
	search_fields = ('location', 'rutf_reporter')
	actions = ['allow_late_report', 'deny_late_report']

	def allow_late_report(self, request, queryset):
                #rows_updated = queryset.update(accept_late_report = True)

                allowed_reporters = []
                reporters_messages = []
                today = datetime.now()
                new_deadline = None
                message = "Please send your report before %s"
                for late_healthpost in queryset:
                    late_healthpost.accept_late_report = True
                    late_healthpost.save()

                    # new deadline
                    new_deadline = today + timedelta(days=int(late_healthpost.extended_days))
                    reporters_messages.append({"reporter": late_healthpost.rutf_reporter, "message":message % new_deadline})
                    allowed_reporters.append(late_healthpost.rutf_reporter)

                    EventSchedule.objects.create(callback='rutfet.utils.deny_allowed_health_posts',
                                                months=set([new_deadline.month]),
                                                days_of_month=set([new_deadline.day]),
                                                hours = set([0]),
                                                minutes=set([0]),
                                                callback_kwargs = {"late_healthpost":late_healthpost})
                    

                # send message to the reporter to
                # report with the extended days
                send_text_message(reporters_messages = reporters_messages)
                
                rows_updated = len(allowed_reporters)                  

                # Display message to the user
                if rows_updated ==1:
                    message_no = "1 health post was"
                elif rows_updated > 1:
                    message_no = "%s health posts were" % rows_updated

                self.message_user(request, "%s allowed to report late" % message_no)
                

        def deny_late_report(self, request, queryset):
                rows_updated = queryset.update(accept_late_report = False)

                # Display message to the user
                if rows_updated ==1:
                    message_no = "1 health post was"
                elif rows_updated > 1:
                    message_no = "%s health posts were" % rows_updated

                self.message_user(request, "%s denied to report late" % message_no)

		
        
class AlertAdmin(admin.ModelAdmin):
	list_display = ('rutf_reporter', 'notice', 'time', 'resolved')
	list_filter = ['resolved',]
	date_hierarchy = 'time'
	ordering = ['resolved']
	actions = ['resolve_alert', 'unresolve_alert','delete_selected']

	def queryset(self, request):
                qs = super(AlertAdmin, self).queryset(request)
                webuser = WebUser.by_user(request.user)
                webuser_location = webuser.location
                if webuser_location is not None:
                    child_locations = webuser_location.descendants(include_self = True)
                    #Select RUTF Reporters from the same location as the web-user
                    rutf_reporters = RUTFReporter.objects.filter(location__in = child_locations)
                    return qs.filter(rutf_reporter__in = rutf_reporters)
                else:
                    return qs
            

        def resolve_alert(self, request, queryset):
                rows_updated = queryset.update(resolved = True)

                # Display message to the user
                if rows_updated ==1:
                    message_no = "1 alert was"
                elif rows_updated > 1:
                    message_no = "%s alerts were" % rows_updated

                self.message_user(request, "%s sucessfully set to resloved state" % message_no)
                

        def unresolve_alert(self, request, queryset):
                rows_updated = queryset.update(resolved = False)

                # Display message to the user
                if rows_updated ==1:
                    message_no = "1 alert was"
                elif rows_updated > 1:
                    message_no = "%s alerts were" % rows_updated

                self.message_user(request, "%s sucessfully set to unresloved state" % message_no)

        
        def delete_view(self, request, object_id, extra_context=None):
                # if request.POST is set, the user already confirmed deletion
                if not request.POST:
                    self.message_user(request, "my delete message")
                #super(MyModelAdmin, self).delete_view(request, object_id, extra_context)



class SupplyAdmin(admin.ModelAdmin):
	list_display = ('name', 'code', 'unit')
	
        #pass

class SupplyPlaceAdmin(admin.ModelAdmin):
	list_display = ('location', 'supply', 'quantity')
	radio_fields = {'supply' : admin.HORIZONTAL}

	def queryset(self, request):
                qs = super(SupplyPlaceAdmin, self).queryset(request)
                webuser = WebUser.by_user(request.user)
                webuser_location = webuser.location
                child_locations = webuser_location.descendants(include_self = True)
                                               
                return qs.filter(location__in = child_locations)


class DeletedItemsAdmin(admin.ModelAdmin):
        list_display = ('model_name', 'object_id', 'content_object')
        list_filter = ('model_name',)
        #actions = ['delete_selected',]
        #   delete_selected.short_description = u'Delete Item Permanently'



class WebUserAddForm( UserCreationForm ):
	class Meta:
		model = WebUser
		
	def __init__(self, *args, **kwargs):
                return super(WebUserAddForm,self).__init__( *args, **kwargs)
        

class WebUserAdminForm(forms.ModelForm):
	class Meta:
		model = WebUser
	password = forms.CharField( help_text=_("Use '[algo]$[salt]$[hexdigest]' or use the <a href=\"password/\">change password form</a>."))


class WebUserAdmin( UserAdmin ):
        list_display = ('username', 'first_name', 'last_name')

        #fields = ('location',)
	#form = WebUserAdminForm
        #add_form = WebUserForm
	
admin.site.register(WebUser, WebUserAdmin )



# add our models to the django admin
##admin.site.register(RUTFReporter, RUTFReporterAdmin)

admin.site.register(Role)
admin.site.register(RUTFReporter, RUTFReporterAdmin)
admin.site.register(Supply, SupplyAdmin)
admin.site.register(HealthPost, HealthPostAdmin)
#admin.site.register(SupplyPlace, SupplyPlaceAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(LateHealthPost, LateHealthPostAdmin)
admin.site.register(DeletedItems, DeletedItemsAdmin)

#admin.site.register(WebUser)

#admin.site.register(ReportPeriod)

admin.site.disable_action('delete_selected')
