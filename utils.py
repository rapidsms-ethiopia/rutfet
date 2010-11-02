from datetime import datetime, timedelta
import calendar
from django.utils.text import capfirst
from django.utils import translation
from models import *
from locations.models import *
import xlwt
from cStringIO import StringIO

# Messaging function to send message
from rapidsms.contrib.messaging.utils import send_message
from rapidsms.contrib.scheduler.models import EventSchedule

import pygsm
import settings

# Ethiopian Months in their order
ethipian_month = {"1":"Meskerem", "2":"Tekemte", "3":"Hedare", "4":"Tahesas",
                  "5":"Tere", "6":"Yekatit", "7":"Megabit", "8":"Meyaziya",
                  "9":"Genbot", "10":"Sene", "11":"Hamle", "12":"Nehase", "13":"Pagmen"}


# if the reporiting is done Monthly, then the current reporting period
# is from 1st to 7th date of the next month
def current_reporting_period():
	"""Return a month, year, period start date value of the current reporting
        period. """

	month = ""
	year = ""
	late = False
	start_date = None
        end_date = None
        reporting_start_date = None
        reporting_start_date = None
        
	current_datetime_gc = datetime.now()
	current_month_gc = current_datetime_gc.month
        current_day_gc = current_datetime_gc.day
        current_year_gc = current_datetime_gc.year
        
        # if the month is march, april, may, ... or August
        # leap year and Non-leap year start dates are similar
	if current_month_gc == 3:
                # Reporting period is month "Yekatit"
                month = ethipian_month["6"]
                year = current_year_gc - 8
                start_date = datetime(current_year_gc, current_month_gc - 1, 8)
                if current_day_gc  in range(10,17):
                        late = False
                else:
                        if current_day_gc in range(1,10):
                                month = ethipian_month["5"]
                                year = current_year_gc - 8
                                if calendar.isleap(current_year_gc):
                                        start_date = datetime(current_year_gc, current_month_gc - 2, 10)
                                else:
                                        start_date = datetime(current_year_gc, current_month_gc - 2, 9)
                        else:
                                # date range is from 14 to 30(31)
                                # value is already assigned
                                pass 
                        late = True
                        
                
        elif current_month_gc == 4:
                # Reporting period is month "Megabit"
                month = ethipian_month["7"]
                year = current_year_gc - 8
                start_date = datetime(current_year_gc, current_month_gc - 1, 10)
                if current_day_gc in range(9,16):
                        late = False
                else:
                        if current_day_gc in range(1,9):
                                month = ethipian_month["6"]
                                year = current_year_gc - 8
                                start_date = datetime(current_year_gc, current_month_gc - 2, 8)
                        else:
                                # date range is from 14 to 30(31)
                                # value is already assigned
                                pass 
                        late = True
                
        elif current_month_gc == 5:
                # Reporting period is month "Meyaziya"
                month = ethipian_month["8"]
                year = current_year_gc - 8
                start_date = datetime(current_year_gc, current_month_gc - 1, 9)
                if current_day_gc in range(9,16):
                        late = False
                else:
                        if current_day_gc in range(1,9):
                                month = ethipian_month["7"]
                                year = current_year_gc - 8
                                start_date = datetime(current_year_gc, current_month_gc - 2, 10)
                        else:
                                # date range is from 14 to 30(31)
                                # value is already assigned
                                pass 
                        late = True
                
        elif current_month_gc == 6:
                # Reporting Period is month "Genbot"
                month = ethipian_month["9"]
                year = current_year_gc - 8
                start_date = datetime(current_year_gc, current_month_gc - 1, 9)
                if current_day_gc in range(8,15):
                        late = False
                else:
                        if current_day_gc in range(1,8):
                                month = ethipian_month["8"]
                                year = current_year_gc - 8
                                start_date = datetime(current_year_gc, current_month_gc - 2, 9)
                        else:
                                # date range is from 14 to 30(31)
                                # value is already assigned
                                pass 
                        late = True
                
        elif current_month_gc == 7:
                # Reporting period is month "Sene"
                month = ethipian_month["10"]
                year = current_year_gc - 8
                start_date = datetime(current_year_gc, current_month_gc - 1, 8)
                if current_day_gc in range(8,15):
                        late = False
                else:
                        if current_day_gc in range(1,8):
                                month = ethipian_month["9"]
                                year = current_year_gc - 8
                                start_date = datetime(current_year_gc, current_month_gc - 2, 9)
                        else:
                                # date range is from 14 to 30(31)
                                # value is already assigned
                                pass 
                        late = True
                
        elif current_month_gc == 8:
                # Reporting period is month "Hamle"
                month = ethipian_month["11"]
                year = current_year_gc - 8
                start_date = datetime(current_year_gc, current_month_gc - 1, 8)
                if current_day_gc in range(7,14):
                        late = False
                else:
                        if current_day_gc in range(1,7):
                                month = ethipian_month["10"]
                                year = current_year_gc - 8
                                start_date = datetime(current_year_gc, current_month_gc - 2, 8)
                        else:
                                # date range is from 14 to 30(31)
                                # value is already assigned
                                pass                                     
                                        
                        late = True
                        

        # if the month is September, october, ... or February
        # leap year and Non-leap year month start dates are different
        elif current_month_gc == 1:
                # Check if the Current year is leap year for
                # gregorian calender. if it is leap year
                # then the previous ethipian year is leap year
                month = ethipian_month["4"]
                year = current_year_gc - 8
                if calendar.isleap(current_year_gc) and current_day_gc in range(10, 17):
                        start_date = datetime(current_year_gc - 1, 12, 11)
                        late = False                        
                elif (not calendar.isleap(current_year_gc)) and current_day_gc in range(9, 16):
                        start_date = datetime(current_year_gc - 1, 12, 10)
                        late = False
                else:
                        if calendar.isleap(current_year_gc)and current_day_gc in range(1, 10):
                                month = ethipian_month["3"]
                                year = current_year_gc - 8
                                if calendar.isleap(current_year_gc):
                                        start_date = datetime(current_year_gc - 1, 11, 11)
                                else:
                                        start_date = datetime(current_year_gc - 1, 11, 10)
                                        
                        elif (not calendar.isleap(current_year_gc)) and current_day_gc in range(1, 9):
                                month = ethipian_month["3"]
                                year = current_year_gc - 8
                                if calendar.isleap(current_year_gc):
                                        start_date = datetime(current_year_gc - 1, 11, 11)
                                else:
                                        start_date = datetime(current_year_gc - 1, 11, 10)
                                        
                        else:
                                if calendar.isleap(current_year_gc):
                                        start_date = datetime(current_year_gc - 1, 12, 11)
                                else:
                                        start_date = datetime(current_year_gc - 1, 12, 10)
                        
                        late = True
                        
                        
        elif current_month_gc == 2:
                # Check if the Current year is leap year for
                # gregorian calender. if it is leap year
                # then the previous ethipian year is leap year
                month = ethipian_month["5"]
                year = current_year_gc - 8
                if calendar.isleap(current_year_gc)and current_day_gc in range(9, 15):
                        start_date = datetime(current_year_gc, current_month_gc - 1, 10)
                        late = False 
                elif (not calendar.isleap(current_year_gc)) and current_day_gc in range(8, 15):
                        start_date = datetime(current_year_gc, current_month_gc - 1, 9)
                        late = False
                else:
                        if calendar.isleap(current_year_gc)and current_day_gc in range(1, 9):
                                month = ethipian_month["4"]
                                year = current_year_gc - 8
                                if calendar.isleap(current_year_gc):
                                        start_date = datetime(current_year_gc - 1, 12, 11)
                                else:
                                        start_date = datetime(current_year_gc - 1, 12, 10)
                        elif (not calendar.isleap(current_year_gc)) and current_day_gc in range(1, 8):
                                month = ethipian_month["4"]
                                year = current_year_gc - 8
                                if calendar.isleap(current_year_gc):
                                        start_date = datetime(current_year_gc - 1, 12, 11)
                                else:
                                        start_date = datetime(current_year_gc - 1, 12, 10)
                                        
                        else:
                                if calendar.isleap(current_year_gc):
                                        start_date = datetime(current_year_gc, current_month_gc - 1, 10)
                                else:
                                        start_date = datetime(current_year_gc, current_month_gc - 1, 9)
                        late = True
                        
        elif current_month_gc == 9:
                # Check if the next year is leap year for
                # gregorian calender. if it is leap year
                # then the previous ethipian year is leap year
                month = ethipian_month["12"]
                year = current_year_gc - 8
                next_year_gc = current_year_gc + 1
                if calendar.isleap(next_year_gc)and current_day_gc in range(12, 19):
                        start_date = datetime(current_year_gc, current_month_gc - 1, 7)
                        late = False
                elif (not calendar.isleap(next_year_gc)) and current_day_gc in range(11, 18):
                        start_date = datetime(current_year_gc, current_month_gc - 1, 7)
                        late = False
                else:
                        if calendar.isleap(next_year_gc)and current_day_gc in range(1, 12):
                                month = ethipian_month["11"]
                                year = current_year_gc - 8
                                start_date = datetime(current_year_gc, current_month_gc - 2, 8)
                                                                        
                        elif (not calendar.isleap(next_year_gc)) and current_day_gc in range(1, 11):
                                month = ethipian_month["11"]
                                year = current_year_gc - 8
                                start_date = datetime(current_year_gc, current_month_gc - 2, 8)
                                        
                        else:
                                start_date = datetime(current_year_gc, current_month_gc - 1, 7)
                                
                        late = True
                        
        elif current_month_gc == 10:
                # Check if the next year is leap year for
                # gregorian calender. if it is leap year
                # then the previous ethipian year is leap year
                month = ethipian_month["1"]
                year = current_year_gc - 7
                start_date = datetime(current_year_gc, current_month_gc - 1, 11)
                next_year_gc = current_year_gc + 1
                if calendar.isleap(next_year_gc)and current_day_gc in range(12, 19):
                        start_date = datetime(current_year_gc, current_month_gc - 1, 12)
                        late = False
                elif (not calendar.isleap(next_year_gc)) and current_day_gc in range(11, 18):
                        start_date = datetime(current_year_gc, current_month_gc - 1, 11)
                        late = False
                else:
                        if calendar.isleap(next_year_gc)and current_day_gc in range(1, 12):
                                month = ethipian_month["12"]
                                year = current_year_gc - 8
                                if calendar.isleap(next_year_gc):
                                        start_date = datetime(current_year_gc, current_month_gc - 2, 7)
                                else:
                                        start_date = datetime(current_year_gc, current_month_gc - 2, 6)
                                        
                        elif (not calendar.isleap(next_year_gc)) and current_day_gc in range(1, 11):
                                month = ethipian_month["12"]
                                year = current_year_gc - 8
                                if calendar.isleap(next_year_gc):
                                        start_date = datetime(current_year_gc, current_month_gc - 2, 7)
                                else:
                                        start_date = datetime(current_year_gc, current_month_gc - 2, 7)
                                        
                        else:
                                if calendar.isleap(next_year_gc):
                                        start_date = datetime(current_year_gc, current_month_gc - 1, 12)
                                else:
                                        start_date = datetime(current_year_gc, current_month_gc - 1, 11)
                        late = True
                        
        elif current_month_gc == 11:
                # Check if the next year is leap year for
                # gregorian calender. if it is leap year
                # then the previous ethipian year is leap year
                month = ethipian_month["2"]
                year = current_year_gc - 7
                next_year_gc = current_year_gc + 1
                if calendar.isleap(next_year_gc)and current_day_gc in range(11, 18):
                        start_date = datetime(current_year_gc, current_month_gc - 1, 12)
                        late = False
                elif (not calendar.isleap(next_year_gc)) and current_day_gc in range(10, 17):
                        start_date = datetime(current_year_gc, current_month_gc - 1, 11)
                        late = False
                else:
                        if calendar.isleap(next_year_gc)and current_day_gc in range(1, 11):
                                month = ethipian_month["1"]
                                year = current_year_gc - 7
                                if calendar.isleap(next_year_gc):
                                        start_date = datetime(current_year_gc, current_month_gc - 2, 12)
                                else:
                                        start_date = datetime(current_year_gc, current_month_gc - 2, 11)
                                        
                        elif (not calendar.isleap(next_year_gc)) and current_day_gc in range(1, 10):
                                month = ethipian_month["1"]
                                year = current_year_gc - 7
                                if calendar.isleap(next_year_gc):
                                        start_date = datetime(current_year_gc, current_month_gc - 2, 12)
                                else:
                                        start_date = datetime(current_year_gc, current_month_gc - 2, 11)
                                        
                        else:
                                if calendar.isleap(next_year_gc):
                                        start_date = datetime(current_year_gc, current_month_gc - 1, 12)
                                else:
                                        start_date = datetime(current_year_gc, current_month_gc - 1, 11)
                        late = True
                        
        elif current_month_gc == 12:
                # Check if the next year is leap year for
                # gregorian calender. if it is leap year
                # then the previous ethipian year is leap year
                month = ethipian_month["3"]
                year = current_year_gc - 7
                next_year_gc = current_year_gc + 1
                if calendar.isleap(next_year_gc)and current_day_gc in range(11, 18):
                        start_date = datetime(current_year_gc, current_month_gc - 1, 11)
                        late = False                        
                elif (not calendar.isleap(next_year_gc)) and current_day_gc in range(10, 17):
                        start_date = datetime(current_year_gc, current_month_gc - 1, 10)
                        late = False
                else:
                        if calendar.isleap(next_year_gc)and current_day_gc in range(1, 11):
                                month = ethipian_month["2"]
                                year = current_year_gc - 7
                                next_year_gc = current_year_gc + 1
                                if calendar.isleap(next_year_gc):
                                        start_date = datetime(current_year_gc, current_month_gc - 2, 12)
                                else:
                                        start_date = datetime(current_year_gc, current_month_gc - 2, 11)
                                        
                        elif (not calendar.isleap(next_year_gc)) and current_day_gc in range(1, 10):
                                month = ethipian_month["2"]
                                year = current_year_gc - 7
                                next_year_gc = current_year_gc + 1
                                if calendar.isleap(next_year_gc):
                                        start_date = datetime(current_year_gc, current_month_gc - 2, 12)
                                else:
                                        start_date = datetime(current_year_gc, current_month_gc - 2, 11)
                                        
                        else:
                                if calendar.isleap(next_year_gc):
                                        start_date = datetime(current_year_gc, current_month_gc - 1, 11)
                                else:
                                        start_date = datetime(current_year_gc, current_month_gc - 1, 10)
                        late = True

        next_year_gc = current_year_gc + 1
        if current_month_gc == 9:
                # inculde both the 12th and 13th month together
                next_year_gc = current_year_gc + 1
                if calendar.isleap(next_year_gc) and current_day_gc in range(12, 19):
                        end_date = datetime(current_year_gc, current_month_gc, 11, 23, 59, 59)
                elif (not calendar.isleap(next_year_gc)) and current_day_gc in range(11, 18):
                        end_date = datetime(current_year_gc, current_month_gc, 10, 23, 59, 59)
                else:
                        end_date = start_date + timedelta(days=29,hours=23,minutes=59,seconds=59)
                        
        elif current_month_gc == 10 and calendar.isleap(next_year_gc) and current_day_gc in range(1, 12):
                end_date = datetime(current_year_gc, current_month_gc - 1, 11, 23, 59, 59)
                
        elif current_month_gc == 10 and  (not calendar.isleap(next_year_gc)) and current_day_gc in range(1, 11):
                end_date = datetime(current_year_gc, current_month_gc - 1, 10, 23, 59, 59)
    
        else:
                end_date = start_date + timedelta(days=29,hours=23,minutes=59,seconds=59)

        reporting_start_date = end_date + timedelta(seconds=1)
        reporting_end_date = reporting_start_date + timedelta(days=6,hours=23,minutes=59,seconds=59)

        # compile start dates and end dates as tuple
        dates_gc = (start_date, end_date, reporting_start_date, reporting_end_date)
	
	# return a tuple
	return (month, year, late, dates_gc)


def get_or_generate_reporting_period():
        # Get or Generate reporting period
        month, year, late , dates_gc = current_reporting_period()
        start_date = dates_gc[0]
        end_date = dates_gc[1]
        reporting_start_date = dates_gc[2]
        reporting_end_date = dates_gc[3]

              
        
        period = ReportPeriod.objects.filter(
                month = month,
                year = year)

        if len(period) == 0:
                first_reminder_date = (reporting_end_date - timedelta(days=2))
                second_reminder_date = (reporting_end_date - timedelta(days=1))
                third_reminder_date = reporting_end_date
                
                EventSchedule.objects.all().delete()
                EventSchedule.objects.create(callback='rutfet.utils.firstReminder',
                                                months=set([first_reminder_date.month]),
                                                days_of_month=set([first_reminder_date.day]),
                                                hours = set([8]),
                                                minutes=set([0]))
                EventSchedule.objects.create(callback='rutfet.utils.secondReminder',
                                                months=set([second_reminder_date.month]),
                                                days_of_month=set([second_reminder_date.day]),
                                                hours = set([8]),
                                                minutes=set([0]))
                EventSchedule.objects.create(callback='rutfet.utils.thirdReminder',
                                                months=set([third_reminder_date.month]),
                                                days_of_month=set([third_reminder_date.day]),
                                                hours = set([8]),
                                                minutes=set([0]))

                # schedule selecting and storing late healthposts in the next day of the deadline date
                # first clear the the database
                LateHealthPost.objects.all().delete()
                late_report_start_date = (reporting_end_date + timedelta(seconds=1))
                EventSchedule.objects.create(callback='rutfet.utils.store_late_healthposts',
                                                months=set([late_report_start_date.month]),
                                                days_of_month=set([late_report_start_date.day]),
                                                hours = set([8]),
                                                minutes=set([0]))
                
                ReportPeriod.objects.create(
                        month = month,
                        year = year,
                        start_date = start_date,
                        end_date = end_date,
                        reporting_start_date = reporting_start_date,
                        reporting_end_date = reporting_end_date)
                return ReportPeriod.objects.latest()
        else:
                return period[0]

                
       

def get_model_lists():
        from django.utils.text import capfirst
	from django.utils.html import escape
	from django.contrib import admin
	
	def no_auto_fields(field):
		from django.db import models
		return not isinstance(field[2], models.AutoField)
	
	excluded_models = [Role, SupplyPlace, LateHealthPost]
	models = []	
	for model, m_admin in admin.site._registry.items():
		
		# fetch ALL fields (including those nested via
		# foreign keys) for this model
		
		fields = [{ "caption": escape(capt), "name": name, "help_text": field.help_text }
			for name, capt, field in filter(no_auto_fields, nested_fields(model))]
		
		# pass model metadata and fields array
		# to the template to be rendered

		#select models only related to rutfet
		if model._meta.app_label == "rutfet" and model not in excluded_models:
                        models.append({
                                "caption": capfirst(model._meta.verbose_name_plural),
                                "name":    model.__name__.lower(),
                                "app_label": model._meta.app_label,
                                "fields": fields
                        })

        return models


def nested_fields(model, max_depth=2):
        
	def iterate(model, nest=None):
		fields = []
		
		# iterate all of the fields in this model, and recurse
		# each foreign key to include fields from nested models

                # For Each model, exculde unrequired fileds

                if model == Entry:
                        exculded_field_name = ["time"]
                        filtered_fields = [field for field in model._meta.fields if field.name not in exculded_field_name]
                        
                elif model == RUTFReporter: #or model == Reporter:
                        exculded_field_name = ["alias", "language", "registered_self", "email", "reporter_ptr", "grandfather_name", "phone"]
                        filtered_fields = [field for field in model._meta.fields if field.name not in exculded_field_name]
                        
                elif model == HealthPost or model == Location:
                        exculded_field_name = ["parent", "latitude", "longitude", "location_ptr"]
                        filtered_fields = [field for field in model._meta.fields if field.name not in exculded_field_name]
                        
                elif model == Supply:
                        exculded_field_name = ["unit",]
                        filtered_fields = [field for field in model._meta.fields if field.name not in exculded_field_name]
                elif model == WebUser:
                        # included fields
                        included_field_name = ["username", "first_name", "last_name", "email", "location"]
                        filtered_fields = [field for field in model._meta.fields if field.name in included_field_name]
                #elif model == Alert:
                        #exculded_field_name = ["unit",]
                        #filtered_fields = [field for field in model._meta.fields if field.name not in exculded_field_name]
                elif model == Role:
                        exculded_field_name = ["code",]
                        filtered_fields = [field for field in model._meta.fields if field.name not in exculded_field_name]
                elif model == SupplyPlace:
                        exculded_field_name = ["quantity",]
                        filtered_fields = [field for field in model._meta.fields if field.name not in exculded_field_name]
                       
                else:
                        filtered_fields = model._meta.fields
		
		for field in filtered_fields:
			if nest is None: my_nest = [field]
			else: my_nest = nest + [field]
			
			# is this a foreign key? (also abort if depth is too deep)
			if (hasattr(field, "rel")) and (field.rel is not None) and (len(my_nest) <= max_depth):
				fields.extend(iterate(field.rel.to, my_nest))
			
			# add the field object as a tuple, including the
			# caption (containing prefixes) and the class itself
			else:
				filter = "__".join([f.name for f in my_nest])
				#label = "/".join([capfirst(translation.ungettext(f.verbose_name, "", 1)) for f in my_nest])
				label = " ".join([capfirst(translation.ungettext(f.verbose_name, "", 1)) for f in my_nest])
				fields.append((filter, label, field))
		
		return fields

	# start processing at the top
	return iterate(model)





def create_excel(context_dict):

    """
    Creates an Excel document of a report.

    It accepts one argument, the context_dict from views.report_view.

    It returns a string of data containing the Excel document, which can
    be written to a response.
    """

    header_style = xlwt.XFStyle()
    header_style.font.bold = True
    header_style.font.height = 160
    header_style.alignment.horz = xlwt.Alignment.HORZ_CENTER
    header_style.alignment.wrap = xlwt.Alignment.WRAP_AT_RIGHT

    normal_style = xlwt.XFStyle()

    PINK = 14
    incomplete_style = xlwt.XFStyle()
    incomplete_style.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    incomplete_style.pattern.pattern_fore_colour = PINK

    wb = xlwt.Workbook()
    ws = wb.add_sheet(context_dict['report_title'], cell_overwrite_ok = True)
    ws.row(0).height = 420
    c = 0
    

    
    for column in context_dict['columns']:
        ws.write(0, c, column['name'], header_style)
        c += 1

    r = 1
    for row in context_dict['rows']:
        style = normal_style
        c = 0
        for cell in row['cells']:
            #ws.write(r, c, unicode(cell_value), style)
            ws.write(r, c, unicode(cell['value']), style)
            c += 1
        r += 1

    temp_buffer = StringIO()
    wb.save(temp_buffer)
    return temp_buffer.getvalue()




## Modified code to send sms using pygsm

def send_text_message(reporters = None, message = None, reporters_messages = None):
	
	# mass SMS sender is used to send a message to a
	# list of reporters.
	
	success = 0
	reporter_received = []
	reporter_not_received = []

        # send personalized message reporters
        # reporter_message is list of dictionary dictionary data type.
        # the dictioanry has "reporter" and "message" keys
        
        if reporters_messages is not None:
                for reporter_message in reporters_messages:
                        try:
                                connection = reporter_message["reporter"].default_connection
                                send_message(connection, reporter_message["message"])
                                success += 1
                                reporter_received.append(reporter_message["reporter"])
                        except Exception, e:
                                pass

                for reporter_message in reporters_messages:
                        if reporter_message["reporter"] not in reporter_received:
                                reporter_not_received.append(reporter_message["reporter"])
        
                
        else:
                # a message to list of reporters 
                for reporter in reporters:
                        try:
                                connection = reporter.default_connection
                                send_message(connection, message)
                                success += 1
                                reporter_received.append(reporter)
                        except Exception, e:
                                pass
                                #print e
                
                reporter_not_received = filter(lambda reporters: reporters not in reporter_received, reporters)
                
        return (message, reporter_received, reporter_not_received)




def get_late_reporters():
        current_period = get_or_generate_reporting_period()
        start,end = (current_period.reporting_start_date,current_period.reporting_end_date)
        #current_entries = Entry.objects.filter(time__range=(start,end))
        current_entries = Entry.objects.filter(report_period = current_period)
        health_posts = HealthPost.objects.filter(type__name='health post')
        submitted_healthposts=[]
        late_reporters=[]
        #get health posts who has successfully sent their report.
        for entry in current_entries:
                submitted_healthposts.append(entry.supply_place.location)
                
        #filter out the health posts who hasn't yet sent their report.  
        late_healthpost = filter(lambda health_posts: health_posts not in submitted_healthposts, health_posts)

        for healthpost in late_healthpost:
                late_reporters.append(healthpost.reporters)

        all_late_reporters = []
        for late_reporter in late_reporters:
                for reporter in late_reporter:
                        all_late_reporters.append(reporter)

        # finanlly filter active reporters
        all_late_reporters = filter(lambda all_late_reporters:
                                    all_late_reporters.is_active_reporter == True, all_late_reporters)
        
        return all_late_reporters




def firstReminder(router):
    month, year, late , dates_gc = current_reporting_period()
    first_reminder_message = "You haven't reported data for, %s-%s. Please send your report before the deadline" % (month,year)
    send_text_message(self.get_late_reporters(),first_reminder_message)
    
    
    


def secondReminder(router):
    month, year, late , dates_gc = current_reporting_period()
    second_reminder_message = "You haven't reported data for, %s-%s. Please send your report before the deadline" % (month,year)
    send_text_message(self.get_late_reporters(),second_reminder_message)
    
    


def finalReminder(router):
    month, year, late , dates_gc = current_reporting_period()
    third_reminder_message = "You haven't reported data for, %s-%s. Please send your report before the deadline" % (month,year)
    send_text_message(self.get_late_reporters(),third_reminder_message)


def store_late_healthposts(router):
        """ Filter healthposts from which report is not made in the given
        period and store it in the LateHealtPost model """

        current_period = get_or_generate_reporting_period()
        late_healthposts = HealthPost.get_late_healthposts(current_period)

        # First clear the previous entries from latehealthposts model
        # LateHealthPost.objects.all().delete()

        # store late health posts and their reporters in LateHealthPost model
        for late_healthpost in late_healthposts:
                reporters = late_healthpost.reporters
                for reporter in reporters:
                        # add active reporters only
                        if reporter.is_active_reporter == True:
                                LateHealthPost.objects.create(
                                        location = late_healthpost,
                                        rutf_reporter = reporter)

def deny_allowed_health_posts(router, late_healthpost):
        """ Deny allowed health posts at the end of the new deadline """

        # set allow_late_report to False

        try:
                
                late_health_post = LateHealthPost.objects.get(location = late_healthpost.location)
                late_health_post.accept_late_report = False
                late_health_post.save()
                #print "************ Testing Allow Health Post..."
                print health_post.name
        except Exception, e:
                print e
                                
