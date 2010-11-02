#!/usr/bin/env python
# vim: noet

from django.contrib.auth.decorators import login_required, permission_required
from datetime import datetime, timedelta
import fpformat
import os
import sys
import math

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.management import setup_environ

from models import *
from tables import *
from utils import * 

from scope import *

from django.utils.datastructures import SortedDict

#from matplotlib.backends.backend_agg import FigureCanvasAgg as  FigureCanvas
from matplotlib.figure import Figure
import numpy as np
#import matplotlib as mpl
#import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['font.size'] = 10
#import pylab as plt
import matplotlib.pyplot as plt


from django.core.paginator import Paginator, InvalidPage, EmptyPage




@login_required
@define_scope
def send_sms(request, scope, reporter_id = None):

        not_received = False
        reporters_not_received = []
        not_received_reporter_id = []
        sms_text = ""

        if request.method == "POST":
                
                sms_text = request.POST['text_message'].replace('\n', '')
                #phone_numbers = request.POST['phone_number_list'].split(";")
                recipients = []
                reporters = scope.rutf_reporters()
                for reporter in reporters:
                        if request.POST.has_key("reporter-id-" + str(reporter.pk)):
                                recipients.append(reporter)

                # create a temporary connection object for the phone number lists
                (message, reporter_received, reporter_not_received) = send_text_message(recipients, sms_text)

                if len(reporter_not_received) != 0:
                        # some reporters don't receive the message
                        not_received = True
                        reporters_not_received = reporter_not_received
                        not_received_reporter_id = [reporter.id for reporter in reporter_not_received]
                        
                        
                        
                
                        
        columns, sub_columns = RUTFReporter.table_columns()
        rows = []
        results = RUTFReporter.aggregate_report(scope = scope)
        
        for result in results:
                row = {}
                row['reporter_id'] = reporter_id = result.pop('reporter_id')
                # filter reporters with phone number
                reporter = RUTFReporter.objects.get(id = reporter_id)
                if not_received:
                        
                        if reporter.phone is not None and reporter.id in not_received_reporter_id:
                                row['cells'] = []
                                row['complete'] = False
                                for value in result.values():
                                        row['cells'].append({'value':value})
                                rows.append(row)
                else:
                        if reporter.phone is not None:
                                row['cells'] = []
                                row['complete'] = True
                                for value in result.values():
                                        row['cells'].append({'value':value})
                                rows.append(row)

        aocolumns_js = "{ \"sType\": \"html\" },"
        for col in columns[1:]:
                if not 'colspan' in col:
                        aocolumns_js += "{ \"asSorting\": [ \"desc\", \"asc\" ], " \
                                    "\"bSearchable\": true },"
        aocolumns_js = aocolumns_js[:-1]

        webuser_location = scope.location
        
        
        return render_to_response('rutf/send_sms.html',
                                  {'columns':columns,
                                   'sub_columns':sub_columns,
                                   'rows':rows,
                                   'aocolumns_js':aocolumns_js,
                                   'webuser_location':webuser_location,
                                   'not_received':not_received,
                                   'reporters_not_received':reporters_not_received,
                                   'sms_text':sms_text},
                                   context_instance=RequestContext(request))


def graph_reporters(scope, webuser, entries_in_currentperiod, reporters):
	# pie chart of RUTF Reporters
	               
        total_reporters = len(reporters)
        reported = 0
        non_reported = 0

        total_currentperiod_entries = len(entries_in_currentperiod)

        # for each report, there is only one reporter
        # and one reporter send a single report in a period

        reported = total_currentperiod_entries
        non_reported = total_reporters - reported

        # Draw the pie chart and save it
        #mpl.rcParams['font.size'] = 8
        plt.figure(figsize = (1.25,1.25), dpi = 100)
        data = [reported,non_reported] 
        labels = ['Reporting HEW/HO', 'Non-reporting HEW/HO']
        colors = ['#0091c7', '#0FBBD0']
        plt.pie(data, colors = colors)
        #plt.legend(labels)

        file_name = "rutfet_reporterpie_wu%s.png" % str(webuser.id)
        chart_path = "rutfet/static/graphs/%s" % str(file_name)
        chart_src_path = "/static/rutfet/graphs/%s" % str(file_name)
        
	plt.savefig(chart_path)
	plt.close()
        
	return chart_src_path
	

def graph_otps():
	# pie chart of health posts
	ent = Entry.objects.all()
	visited = 0
	non_visited = 0
	for e in ent:
		if e.supply_place.type == 'OTP':
			visited += 1

	otps = len(Location.objects.all())
	percent_visited = float(visited)/float(otps)
	percent_not_visited = float(otps - visited)/float(otps)

	chart = PieChart2D(275, 60)
	chart.add_data([(percent_not_visited*100), (percent_visited*100)])
	chart.set_legend(['Non-visited OTPs', 'Visited OTPs'])
	chart.set_colours(['0091C7','0FBBD0'])
	chart.download('rutfet/graphs/otps.png')

	return 'saved otps.png'


@login_required
@define_scope
def filter_reports(request, scope):
        ''' Display filter report page'''

        # webuser's context       
        webuser = WebUser.by_user(request.user)
        webuser_location = webuser.location
        webuser_descendent_locations = []
        if webuser_location is not None:
                webuser_descendent_locations = webuser_location.descendants(include_self = True)
        descendent_location_types = set()
        for location in webuser_descendent_locations: descendent_location_types.add(location.type.name)

        #period context
        periods = ReportPeriod.objects.all()

        #list of models
        models = get_model_lists()
        

        return render_to_response('rutf/filter_report.html',
                                          {'descendent_locations': webuser_descendent_locations,
                                           'location_types': descendent_location_types,
                                           'periods':periods,
                                           'models':models,
                                           'webuser_location':webuser_location,
                                           'model_name':'entry'},
                                          context_instance=RequestContext(request))

        
	

############## Report New with Javascript ##################


@login_required
@define_scope
def reports(request, scope):
        ''' Displays reports in a tabular form.
        the user can also filter reports'''

        # Webuser location
        webuser = WebUser.by_user(request.user)
        webuser_location = webuser.location
        
        dates_GC = {}
        dates_EC = {}
       
        filter_parameters = request.GET
        model_name = filter_parameters['model']
        location_type = filter_parameters['placetype']
        location_name = filter_parameters['placename']
        startmonth_id = filter_parameters['startmonth_id']
        endmonth_id = filter_parameters['endmonth_id']
##        startyear_id = filter_parameters['startyear_id']
##        endyear_id = filter_parameters['endyear_id']
        group_by = filter_parameters['groupby']

        
        # if time range is not given, the report is for all periods
        start_period = ReportPeriod.objects.all().order_by("id")[0]
        end_period = ReportPeriod.objects.all().order_by("-id")[0]
        dates_GC["start"] = start_period.start_date
        dates_GC["end"] = end_period.end_date
        dates_EC["start"] = "%s %s" % (start_period.month, start_period.year)
        dates_EC["end"] = "%s %s" % (end_period.month, end_period.year)
        
        if startmonth_id != "":
                start_period = ReportPeriod.objects.filter(id = int(startmonth_id))[0]
                dates_GC["start"] = start_period.start_date
                dates_EC["start"] = "%s %s" % (start_period.month, start_period.year)
                if endmonth_id != "":
                        end_period = ReportPeriod.objects.filter(id = int(endmonth_id))[0]
                        dates_GC["end"] = end_period.end_date
                        dates_EC["end"] = "%s %s" % (end_period.month, end_period.year)
                else:
                        dates_GC["end"] = start_period.end_date
                        dates_EC["end"] = ""

        # location information
        if location_type != "" and location_name != "":
                location_type_name = "%s %s" % (location_name, location_type)
        else:
                location_type_name = "%s %s" % (webuser_location.name, webuser_location.type.name)

                        
             

        # Get selected model
        app_label = "rutfet"
        model = models.get_model(app_label,model_name)
        report_title = model.TITLE
                        
        #In entry model, aggreagation and grouping is required
        if group_by in ['region', 'zone', 'woreda', 'health post'] and model == Entry:
                columns, sub_columns = model.table_aggregate_columns()
                rows = []
                groups = []
                for hp in scope.health_posts():
                        if group_by == "health post":
                                if hp.type.name.lower() == "health post":
                                        groups.append(hp)
                                        
                        else:
                                groups.append(eval('hp.%s' % group_by))

                # filter out None and redundant values
                groups = set([group for group in groups if group is not None and type(group) == HealthPost])
                       
                for group in groups:
                        row = {}
                        row['cells'] = []
                        row['cells'].append({'value':unicode(group)})
                        results = model.aggregate_report(scope = scope,
                                                 location_type=location_type,
                                                 location_name=location_name,
                                                 startmonth_id = startmonth_id,
                                                 endmonth_id = endmonth_id,
                                                #startyear_id = startyear_id,
                                                #endyear_id = endyear_id,
                                                 group = group)
                        
                        row['complete'] = results.pop('complete')
                        for value in results.values():
                                row['cells'].append({'value': value})

                        rows.append(row)

                title = group_by.title()
                columns.insert(0, {'name': title})
                        
        else:
                columns, sub_columns = model.table_columns()
                rows = []
                results = model.aggregate_report(scope = scope,
                                                 location_type=location_type,
                                                 location_name=location_name,
                                                 startmonth_id = startmonth_id,
                                                 endmonth_id = endmonth_id,
                                                 #startyear_id = startyear_id,
                                                 #endyear_id = endyear_id,
                                                 )
                
                for result in results:
                        row = {}
                        # remove unwanted columns for RUTFReporter and Healthpost
                        if model == RUTFReporter:
                                result.pop("reporter_id")
                        if model == HealthPost:
                                result.pop("healthpost_id")
                        row['cells'] = []
                        # It list values, so by default it is complete
                        row['complete'] = True
                        for value in result.values():
                                row['cells'].append({'value':value})
                        rows.append(row)                

        aocolumns_js = "{ \"sType\": \"html\" },"
        for col in columns[1:]:
                if not 'colspan' in col:
                        aocolumns_js += "{ \"asSorting\": [ \"desc\", \"asc\" ], " \
                                    "\"bSearchable\": true },"
        aocolumns_js = aocolumns_js[:-1]
        
        
        
        
        
        if request.GET.has_key('excel'):
                # export the table to excel document

                context_dict = {'model_name':model_name,
                                'dates': dates_GC,
                                'report_title':report_title,
                                'get_vars': request.META['QUERY_STRING'],
                                'columns':columns,
                                'sub_columns':sub_columns,
                                'rows':rows,
                                'aocolumns_js':aocolumns_js}
                
                
                response = HttpResponse(mimetype="application/vnd.ms-excel")
                filename = "%s %s.xls" % \
                   (report_title, datetime.now().strftime("%d%m%Y"))
                response['Content-Disposition'] = "attachment; " \
                                  "filename=\"%s\"" % filename
                response.write(create_excel(context_dict))
                return response
                
        else:
                return render_to_response('rutf/reports.html',
                                  {'model_name':model_name,
                                   'dates': dates_GC,
                                   'dates_ec': dates_EC,
                                   'report_title':report_title,
                                   'get_vars': request.META['QUERY_STRING'],
                                   'columns':columns,
                                   'sub_columns':sub_columns,
                                   'rows':rows,
                                   'aocolumns_js':aocolumns_js,
                                   'location': location_type_name,
                                   'webuser_location':webuser_location},
                                  context_instance=RequestContext(request))


############ End of Report New with Javascript #############



@login_required
@define_scope
def charts(request, scope):
        ''' Display reported entries in chart form '''

        webuser = WebUser.by_user(request.user)
        webuser_location = webuser.location
        if webuser_location is not None:
                webuser_descendent_locations = webuser_location.descendants(include_self = True)
        descendent_location_types = set()
        for location in webuser_descendent_locations: descendent_location_types.add(location.type.name)


        # By default the chart is created for all
        # periods, so get the periods and their id

        report_periods = ReportPeriod.objects.all().order_by("id")
        #period_start_id = report_periods[0].id
        #period_end_id = report_periods[len(report_periods) -1 ].id
        
        entries = scope.entries()

        location_name = ""
        location_type = ""
        startmonth_id = ""
        endmonth_id = ""
        

        # Get the filter parameter
        if request.method == "POST":
                location_name = request.POST['location_name']
                location_type = request.POST['location_type']
                startmonth_id = request.POST['startmonth_id']
                endmonth_id = request.POST['endmonth_id']

                
                # both parameters are give, filter the data based on the values

                if location_name != "" and location_type != "":
                        # Find location and desendents within the specified location
                        location = HealthPost.objects.filter(name = location_name, type__name = location_type)[0]
                        locations = location.descendants(include_self = True)

                        #entry_ids = [entry.supply_place.location.location_ptr_id for entry in entries]
                        location_id = [location.id for location in locations]

                        entries = filter(lambda entries:
                                       entries.supply_place.location.location_ptr_id in location_id,entries)

                # if time range is given, filter the entries based on the range
                if startmonth_id != "":
                                              
                        if endmonth_id != "":
                                report_periods = filter(lambda report_periods:
                                                        report_periods.id >= int(startmonth_id) and
                                                        report_periods.id <= int(endmonth_id), report_periods)
                                entries = filter(lambda entries: int(startmonth_id) <= entries.report_period.id and
                                                 entries.report_period.id <= int(endmonth_id), entries)
                                
                        else:
                                startmonth_end_date = ReportPeriod.objects.filter(id = startmonth_id)[0].end_date
                                report_periods = filter(lambda report_periods:
                                                        report_periods.id == int(startmonth_id), report_periods)
                                entries = filter(lambda entries: entries.report_period.id == int(startmonth_id) , entries)

                
        # location information
        if location_type != "" and location_name != "":
                location_type_name = "%s %s" % (location_name, location_type)
        else:
                location_type_name = "%s %s" % (webuser_location.name, webuser_location.type.name)

        
        
        # month-year as x-axis label
        months = ["%s \n %s" % (report_period.month, report_period.year)
                  for report_period in report_periods]

        month_ids = [report_period.id  for report_period in report_periods]


        # calculate the sum of consumption in each period
        total_consumption = []
        total_balance = []
        total_admission = []
        #print "month_ids = %s " % month_ids
        for month_id in month_ids:
                total_consumption_per_period = 0
                total_balance_per_period =0
                total_admission_per_period = 0
                #print "entries = %s" %entries
                for entry in entries:
                        if entry.report_period.id == month_id:
                                #print "entry = %s" %entry
                                total_consumption_per_period += entry.consumption
                                total_balance_per_period += entry.balance
                                total_admission_per_period += entry.quantity
                total_consumption.append(total_consumption_per_period)
                total_balance.append(total_balance_per_period)
                total_admission.append(total_admission_per_period)
        
        
        plt.figure(figsize = (9,6.5) ,dpi = 100)
        plt.plot(month_ids, total_admission, label = "Received", marker='*')
	plt.plot(month_ids,total_consumption, label = "Consumption", marker='*')
	plt.plot(month_ids, total_balance, label = "Balance", marker='*')
	plt.xticks(month_ids, months, rotation= 15)
	plt.grid(True)
	month_lable = plt.xlabel('Month')
	plt.ylabel('RUTF Amount')
	plt.legend(loc="upper right")
	#plt.setp(month_lable, fontsize=30)


        file_name = "rutfet_chart_wu%s.png" % webuser.id
        chart_path = "rutfet/static/graphs/%s" % str(file_name)
        chart_src_path = "/static/rutfet/graphs/%s" % str(file_name)
        
	plt.savefig(chart_path)
	plt.close()
        
        return render_to_response('rutf/charts.html',
                                          {'chart_src_path': chart_src_path,
                                           'entries':entries,
                                           'descendent_locations': webuser_descendent_locations,
                                           'location_types': descendent_location_types,
                                           'location':location_type_name,
                                           'periods':ReportPeriod.objects.all().order_by("id"),
                                           'webuser_location':webuser_location},
                                          context_instance=RequestContext(request))
   
##@login_required
##@define_scope
##def map_entries(request, scope):
####	def has_coords(entry):
####		loc = entry.supply_place.location
####		if loc is None: return False
####		return  (loc.latitude is not None) and (loc.longitude is not None)
##		
##
##        entries = scope.entries()
##        webuser = WebUser.by_user(request.user)
##        webuser_location = webuser.location
##        # currently the map is only for two woredas
##        location_types = ["woreda"]
##        location_names = []
##        locations = scope.health_posts()
##        #filter locations which are health posts only
##        healthposts = filter(lambda locations: locations.type.name.lower() == "health post", locations)
##
##        # filter current period entries
##        current_period = get_or_generate_reporting_period()
##        entries_in_currentperiod = filter(lambda entries: entries.report_period == current_period, entries)
##        
##        late_healthposts_all = HealthPost.get_late_healthposts(current_period)       
##        
##        # filter late healthposts within the scope
##        late_healthposts = filter(lambda late_healthposts_all:
##                                  late_healthposts_all in healthposts, late_healthposts_all)
##        
##        result_dic = {"entries": entries_in_currentperiod, "location_types":location_types,
##                      'webuser_location':webuser_location,
##                      'late_healthposts':late_healthposts}
##        
##        woreda_selected = ""
##        if request.method == 'POST':
##        	woreda_selected = request.POST['location_name']
##	
##        if webuser_location is not None:
##                if webuser_location.type.name.lower() == "woreda":
##                        location_names.append(webuser_location.name)
##                        result_dic["location_names"] = location_names
##                        if webuser_location.name.lower() == "haromaya":
##                                return render_to_response("rutf/map_image_haromaya.html",
##                                          result_dic,
##                                          context_instance=RequestContext(request))
##                        
##                        elif webuser_location.name.lower() == "kombolcha":
##                                return render_to_response("rutf/map_image_kombolcha.html",
##                                          result_dic,
##                                          context_instance=RequestContext(request))
##                        
##                else:
##                        location_names.append("Haromaya")
##                        location_names.append("Kombolcha")
##                        result_dic["location_names"] = location_names
##                                                                      
##                        return render_to_response("rutf/map_image_haromaya.html" if woreda_selected.lower() == "haromaya"
##                                                  else "rutf/map_image_kombolcha.html",
##                                                  result_dic,
##                                                  context_instance=RequestContext(request))



@login_required
@define_scope
def map_entries(request, scope):
        
	def has_coords(entry):
		loc = entry.supply_place.location
		if loc is None: return False
		return  (loc.latitude is not None) and (loc.longitude is not None)
		

        webuser_location = scope.location
        # filter current period entries
        entries = scope.entries()
        current_period = get_or_generate_reporting_period()
        entries = filter(lambda entries: entries.report_period == current_period, entries)

        # then filter confimed entries
        if webuser_location.type.name.lower() == "zone":
                entries_confirmed = filter(lambda entries: entries.confirmed_by_woreda == True, entries)
                
        elif webuser_location.type.name.lower() == "region":
                entries_confirmed = filter(lambda entries: entries.confirmed_by_woreda == True and
                                           entries.confirmed_by_zone == True, entries)
                                
        elif webuser_location.type.name.lower() == "federal":
               entries_confirmed = filter(lambda entries: entries.confirmed_by_woreda == True and
                                           entries.confirmed_by_zone == True and
                                          entries.confirmed_by_region == True, entries)
        elif webuser_location.type.name.lower() == "woreda":
                entries_confirmed = entries
        else:
                entries_confirmed = filter(lambda entries: entries.confirmed_by_woreda == True and
                                           entries.confirmed_by_zone == True and
                                          entries.confirmed_by_region == True, entries)
        
        # health posts
        health_posts = scope.health_posts()
        health_posts = filter(lambda health_posts:
                              #health_posts.type.name.lower() == "health post" and
                              (health_posts.latitude is not None) and
                              (health_posts.longitude is not None),
                              health_posts)
##        hp = health_posts[0]
##        print hp
##        print hp.latitude
##        print hp.longitude
##        print hp.reporters_name
        
	entries_with_coordinate = filter(has_coords, entries_confirmed)
	return render_to_response("rutf/map_entries.html",
                                  {"entries": entries_with_coordinate,
                                   "health_posts":health_posts},
                                  context_instance=RequestContext(request))


	

@login_required
@define_scope
def index(request, scope):
        '''Display home page '''
        # Display the index page


        # webuser
        webuser = WebUser.by_user(request.user)
        webuser_location = webuser.location

        get_or_generate_reporting_period()
        #start, end = current_reporting_period()
        month, year, late , dates_gc = current_reporting_period()

        
                
        entries = scope.entries()
        current_period = get_or_generate_reporting_period()
        entries = entries_all = filter(lambda entries: entries.report_period == current_period, entries)

        
        # Confirmed entries by the current web user
        entries_confirmed= []

        not_confirmed_by_woreda = 0
        not_confirmed_by_zone = 0
        not_confirmed_by_region = 0
        descendant_locations = webuser_location.descendants()
                        
        # filter only confirmed entries
        if webuser_location.type.name.lower() == "zone":
                entries = filter(lambda entries: entries.confirmed_by_woreda == True, entries)
                entries_confirmed = filter(lambda entries: entries.confirmed_by_zone == True, entries)

                # number of unconfirmed report by all descendant woredas
                for descendant_location in descendant_locations:
                        if descendant_location.type.name.lower() == "woreda":
                                entries_not_confirmed = filter(lambda entries_all:
                                                               entries_all.confirmed_by_woreda == False and
                                                               entries_all.supply_place.location.woreda.code == descendant_location.code,
                                                               entries_all)
                                
                                not_confirmed_by_woreda += len(entries_not_confirmed)
                                
                
        elif webuser_location.type.name.lower() == "region":
                entries = filter(lambda entries: entries.confirmed_by_zone == True, entries)
                entries_confirmed = filter(lambda entries: entries.confirmed_by_region == True, entries)

                # number of unconfirmed report by all descendant woredas and zones
                
                for descendant_location in descendant_locations:
                        if descendant_location.type.name.lower() == "zone":
                                entries_not_confirmed = filter(lambda entries_all:
                                                               entries_all.confirmed_by_zone == False and
                                                               entries_all.confirmed_by_woreda == True and
                                                               entries_all.supply_place.location.zone.code == descendant_location.code,
                                                               entries_all)
                                not_confirmed_by_zone += len(entries_not_confirmed)

                        if descendant_location.type.name.lower() == "woreda":
                                entries_not_confirmed = filter(lambda entries_all:
                                                               entries_all.confirmed_by_woreda == False and
                                                               entries_all.supply_place.location.woreda.code == descendant_location.code,
                                                               entries_all)
                                                                
                                not_confirmed_by_woreda += len(entries_not_confirmed)


                
        elif webuser_location.type.name.lower() == "federal":
                entries = filter(lambda entries: entries.confirmed_by_region == True, entries)
                #entries_confirmed = filter(lambda entries: entries.confirmed_by_zone == True, entries)

                # number of unconfirmed report by all descendant woredas, zones and regions

                for descendant_location in descendant_locations:
                        if descendant_location.type.name.lower() == "zone":
                                print "************************** loc *****"
                                print descendant_location
                                entries_not_confirmed = filter(lambda entries_all:
                                                               entries_all.confirmed_by_zone == False and
                                                               entries_all.confirmed_by_woreda == True and
                                                               entries_all.supply_place.location.zone.code == descendant_location.code,
                                                               entries_all)
                                print "entries_not_confirmed %s" % entries_not_confirmed
                                not_confirmed_by_zone += len(entries_not_confirmed)

                        if descendant_location.type.name.lower() == "woreda":
                                entries_not_confirmed = filter(lambda entries_all:
                                                               entries_all.confirmed_by_woreda == False and
                                                               entries_all.supply_place.location.woreda.code == descendant_location.code,
                                                               entries_all)
                                                                        
                                not_confirmed_by_woreda += len(entries_not_confirmed)

                        if descendant_location.type.name.lower() == "region":
                                entries_not_confirmed = filter(lambda entries_all:
                                                               entries_all.confirmed_by_region == False and
                                                               entries_all.confirmed_by_zone == True and
                                                               entries_all.confirmed_by_woreda == True and
                                                               entries_all.supply_place.location.region.code == descendant_location.code,
                                                               entries_all)
                                                                        
                                not_confirmed_by_region += len(entries_not_confirmed)
                                        
                
        elif webuser_location.type.name.lower() == "woreda":
                # show all the entries
                entries_confirmed = filter(lambda entries: entries.confirmed_by_woreda == True, entries)
                pass
        else:
                entries = filter(lambda entries: entries.confirmed_by_region == True, entries)

        
        notifications = scope.alerts()
        # filter unresolved notifications only
        notifications = filter(lambda notifications: notifications.resolved == False, notifications)
        reporters = scope.rutf_reporters()

        # draw pie chart to show reporters and non-reporters
        chart_src_path = graph_reporters(scope,webuser, entries, reporters)

        
        locations = scope.health_posts()
        #filter health posts only
        locations = filter(lambda locations:
                           locations.type.name.lower() == "health post", locations)
        
        total_locations = len(locations)
        total_reporters = len(reporters)

        # total number of reports sent in the current period
        total_currentperiod_entries = len(entries)
        healthpost_not_reported = total_locations - total_currentperiod_entries

        # paginaging for notifications
        paginator_alert = Paginator(notifications, 10)

        try:
                page = int(request.GET.get('page', '1'))
        except ValueError:
                page = 1

        try:
              notifications =  paginator_alert.page(page)
        except (InvalidPage, EmptyPage):
              notifications = paginator_alert.page(paginator_alert.num_pages)

        # paginaging for entries
        paginator_entry = Paginator(entries, 10)

        try:
                page = int(request.GET.get('page', '1'))
        except ValueError:
                page = 1

        try:
              entries_in_currentperiod =  paginator_entry.page(page)
        except (InvalidPage, EmptyPage):
              entries_in_currentperiod = paginator_entry.page(paginator_entry.num_pages)


        # if message is sent from the form, send it via send_text_message()
        message = ""
        reporter_received = []
        reporter_not_received = []
        recipients = []
        recipients_name = ""
        reply_sent = False
        if request.method == 'POST':
        	sms_text = request.POST['text_message'].replace('\n', '')
        	reporter_id = int(request.POST['reporer_id'])
        	try:
                        reporter = RUTFReporter.objects.get(id = reporter_id)
                        recipients_name = reporter.first_name
                        recipients.append(reporter)
                        print recipients
                        print reporter.first_name
                        (message, reporter_received, reporter_not_received) = send_text_message(recipients, sms_text)

                        print "**************** Reply *********"
                        print reporter_not_received
                        print reporter_received
                        print "************************"
                        if len(reporter_not_received) == 0 and len(reporter_received) >= 1:
                                reply_sent = True

                                                  
                                
                except Exception, e:
                        print e
                
                      
        return render_to_response('rutf/index.html',
                              {"month":month, "year":year,
                               "entries":entries_in_currentperiod,"notifications":notifications,
                               "entries_num": len(entries),
                               "confirmed_entries_num": len(entries_confirmed),
                               "reporters":reporters, "total_locations":total_locations,
                               "total_reporters":total_reporters,
                               "total_currentperiod_entries":total_currentperiod_entries,
                               "chart_src_path":chart_src_path,
                               "webuser_location":webuser_location,
                               'message':message,
                               "reply_sent":reply_sent,
                               "recipients_name":recipients_name,
                               "healthpost_not_reported":healthpost_not_reported,
                               "not_confirmed_by_woreda":not_confirmed_by_woreda,
                               "not_confirmed_by_zone":not_confirmed_by_zone,
                               "not_confirmed_by_region": not_confirmed_by_region}
                              ,context_instance=RequestContext(request))


@login_required
@define_scope
def reporters(request, scope):
        
        # webuser location
        webuser = WebUser.by_user(request.user)
        webuser_location = webuser.location
        
        columns, sub_columns = RUTFReporter.table_columns()
        rows = []
        results = RUTFReporter.aggregate_report(scope = scope)
        
        for result in results:
                row = {}
                row['reporter_id'] = reporter_id = result.pop('reporter_id')
                row['cells'] = []
                row['cells'].append({'value':result.pop("username"),'link': '/rutf/reporter/%d' % reporter_id})
                row['complete'] = True
                for value in result.values():
                        row['cells'].append({'value':value})
                rows.append(row)                

        aocolumns_js = "{ \"sType\": \"html\" },"
        for col in columns[1:]:
                if not 'colspan' in col:
                        aocolumns_js += "{ \"asSorting\": [ \"desc\", \"asc\" ], " \
                                    "\"bSearchable\": true },"
        aocolumns_js = aocolumns_js[:-1]
        
        
               
        return render_to_response('rutf/reporters.html',
                              {'columns':columns,
                                   'sub_columns':sub_columns,
                                   'rows':rows,
                                   'aocolumns_js':aocolumns_js,
                               'webuser_location':webuser_location}
                              ,context_instance=RequestContext(request))


@login_required
@define_scope
def reporter(request, scope, reporter_id):
        ''' Display detail information about the reporter '''

        # Webuser location
        webuser = WebUser.by_user(request.user)
        webuser_location = webuser.location
        
        rutf_reporter = RUTFReporter.objects.get(id = reporter_id)
        reporter_detail = {}
        
        first_name = rutf_reporter.first_name
        father_name = rutf_reporter.last_name
        grandfather_name = rutf_reporter.grandfather_name
        username = rutf_reporter.user_name
        location = rutf_reporter.place_assigned
        phone = rutf_reporter.phone
        email = rutf_reporter.email
        reporter_detail = {'first_name':first_name, 'father_name':father_name,'grandfather_name':grandfather_name,
                           'username':username, 'location':location, 'phone':phone, 'email':email,}

        # filter entries of the reporter
        entries = scope.entries()
        entries = filter(lambda entries: entries.rutf_reporter == rutf_reporter, entries)

        print "************** reporter ***************"
        print entries

        # filter alerts of the reporter
        alerts = scope.alerts()
        alerts = filter(lambda alerts: alerts.rutf_reporter == rutf_reporter, alerts)
                
        all_entries = []
        for rutf_entry in entries:
                entry = SortedDict()
                entry['period'] = rutf_entry.report_period
                entry['quantity'] = rutf_entry.quantity
                entry['consumption'] = rutf_entry.consumption
                entry['balance'] = rutf_entry.balance
                all_entries.append(entry)
        entry_table = ReporterEntryTable(all_entries, order_by=request.GET.get('sort'))
        entry_rows = entry_table.rows
      
        paginator = Paginator(entry_rows, 10)

        try:
                page = int(request.GET.get('page', '1'))
        except ValueError:
                page = 1

        try:
              entry_rows =  paginator.page(page)
        except (InvalidPage, EmptyPage):
              entry_rows = paginator.page(paginator.num_pages)
              
        reporter_detail['entry_rows'] = entry_rows
        reporter_detail['entry_table'] = entry_table

        all_alerts = []
        for rutf_alert in alerts:
                alert = SortedDict()
                alert['notice'] = rutf_alert.notice
                alert['time'] = rutf_alert.time
                alert['resolved'] = rutf_alert.resolved
                all_alerts.append(alert)
        alert_table = AlertTable(all_alerts, order_by=request.GET.get('sort'))
        alert_rows = alert_table.rows
        
        paginator = Paginator(alert_rows, 10)

        try:
                page = int(request.GET.get('page', '1'))
        except ValueError:
                page = 1

        try:
              alert_rows =  paginator.page(page)
        except (InvalidPage, EmptyPage):
              alert_rows = paginator.page(paginator.num_pages)
              
        reporter_detail['alert_rows'] = alert_rows
        reporter_detail['alert_table'] = alert_table
        
        # add webuser location
        reporter_detail['webuser_location'] = webuser_location
       
        return render_to_response('rutf/reporter.html',
                                  reporter_detail,context_instance=RequestContext(request))
        


@login_required
@define_scope
def healthposts(request, scope):

        # web user location
        webuser = WebUser.by_user(request.user)
        webuser_location = webuser.location
        hp_filter = ""
        healthpost_id_reported = []
        healthpost_id_not_reported = []
        
        if request.method == "GET" and request.GET.has_key('hp_filter'):
                hp_filter = request.GET['hp_filter']
                entries = scope.entries()
                current_period = get_or_generate_reporting_period()
                current_entries = filter(lambda entries: entries.report_period == current_period, entries)
                healthposts = scope.health_posts()
                
                # filter reported health post's id whose report is confirmed
                if webuser_location.type.name.lower() == "zone":
                        healthpost_id_reported = [entry.supply_place.location.id
                                                  for entry in current_entries if entry.confirmed_by_woreda == True]
                        
                elif webuser_location.type.name.lower() == "region":
                        healthpost_id_reported = [entry.supply_place.location.id
                                                  for entry in current_entries if entry.confirmed_by_woreda == True and
                                                  entry.confirmed_by_zone == True]
                        
                elif webuser_location.type.name.lower() == "federal":
                        healthpost_id_reported = [entry.supply_place.location.id
                                                  for entry in current_entries if entry.confirmed_by_woreda == True and
                                                  entry.confirmed_by_zone == True and entry.confirmed_by_region == True]
                elif webuser_location.type.name.lower() == "woreda":
                        healthpost_id_reported = [entry.supply_place.location.id
                                                  for entry in current_entries]
                else:
                        healthpost_id_reported = [entry.supply_place.location.id
                                                  for entry in current_entries if entry.confirmed_by_woreda == True and
                                                  entry.confirmed_by_zone == True and entry.confirmed_by_region == True]

                
                healthpost_id_not_reported = [healthpost.id for healthpost in healthposts
                                              if healthpost.id not in healthpost_id_reported]

                
                               
        columns, sub_columns = HealthPost.table_columns()
        rows = []
        results = HealthPost.aggregate_report(scope = scope)
        
        for result in results:
                row = {}
                row['cells'] = []

                row['complete'] = True
                if hp_filter == "reported":
                        # filter healthposts which report in the current period
                        if result["healthpost_id"] in healthpost_id_reported:
                                row['cells'].append({'value':result.pop("name"),'link': '/rutf/health_post/%d' % result.pop("healthpost_id")})
                                for value in result.values():
                                        row['cells'].append({'value':value})
                                rows.append(row) 

                elif hp_filter == "late":
                        # filter healthposts which don't report in the current period
                        if result["healthpost_id"] in healthpost_id_not_reported:
                                row['cells'].append({'value':result.pop("name"),'link': '/rutf/health_post/%d' % result.pop("healthpost_id")})
                                for value in result.values():
                                        row['cells'].append({'value':value})
                                rows.append(row)
                        
                elif hp_filter == "":
                        row['cells'].append({'value':result.pop("name"),'link': '/rutf/health_post/%d' % result.pop("healthpost_id")})
                        for value in result.values():
                                        row['cells'].append({'value':value})
                        rows.append(row)
                        
                
                               

        aocolumns_js = "{ \"sType\": \"html\" },"
        for col in columns[1:]:
                if not 'colspan' in col:
                        aocolumns_js += "{ \"asSorting\": [ \"desc\", \"asc\" ], " \
                                    "\"bSearchable\": true },"
        aocolumns_js = aocolumns_js[:-1]
                
        return render_to_response('rutf/health_posts.html',
                              {'columns':columns,
                                   'sub_columns':sub_columns,
                                   'rows':rows,
                                   'aocolumns_js':aocolumns_js,
                               'webuser_location':webuser_location}
                              ,context_instance=RequestContext(request))


@login_required
@define_scope
def healthpost(request, scope, healthpost_id):
        ''' Displays a summary of location activities and history '''

        # web user location
        webuser = WebUser.by_user(request.user)
        webuser_location = webuser.location
        
        health_post = HealthPost.objects.get(id=healthpost_id)
        health_post_name = health_post.name
        health_post_type = health_post.type
        reporters= []
        for reporter in health_post.reporters:
                reporters.append({'name':'%s %s' %(reporter.first_name,reporter.last_name),
                                  'phone':reporter.phone,
                                  'is_active':reporter.is_active_reporter})

        entries = scope.entries()
        # filter entries of the reporter
        entries = filter(lambda entries: entries.supply_place.location == health_post, entries)
        all = []
        for rutf_entry in entries:
                entry = SortedDict()
                entry['period'] = rutf_entry.report_period
                entry['quantity'] = rutf_entry.quantity
                entry['consumption'] = rutf_entry.consumption
                entry['balance'] = rutf_entry.balance
                entry['rutf_reporter'] = rutf_entry.rutf_reporter
                all.append(entry)
        table = HealthPostEntryTable(all, order_by=request.GET.get('sort'))
        entry_rows = table.rows
      
        paginator = Paginator(entry_rows, 10)

        try:
                page = int(request.GET.get('page', '1'))
        except ValueError:
                page = 1

        try:
              entry_rows =  paginator.page(page)
        except (InvalidPage, EmptyPage):
              entry_rows = paginator.page(paginator.num_pages)
                

       
        healthpost_detail = {'health_post': health_post,
                             'reporters':reporters,
                             'table':table , 'entry_rows':entry_rows, 'webuser_location':webuser_location}
            


        return render_to_response('rutf/health_post.html',healthpost_detail,context_instance=RequestContext(request))



