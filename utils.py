from datetime import datetime, timedelta
from django.utils.text import capfirst
from django.utils import translation
from models import *
from locations.models import *
from reporters.models import *
import xlwt
from cStringIO import StringIO


# if the reporiting is done weekly, then the current reporting period
# is from monday upto sunday in the same week of the date

def current_reporting_period():
	"""Return a 2-tuple containing datetimes of the start and end
	of the current reporting period (the current calendar week) from monday to sunday"""
	
	# offsets are calculated from today use a datetime, because we
	# want the reporting period to end on the last second of sunday
	today = datetime.today().replace(
		hour=0, minute=0, second=0, microsecond=0)
	
	# reporting period spans the current week, from monday to sunday
	start = today - timedelta(days=today.weekday())
	end   = start + timedelta(days=7) - timedelta(seconds=1)
	
	# return a tuple
	return (start, end)

def get_or_generate_reporting_period():
        # Get or Generate reporting period
        start_date, end_date = current_reporting_period()
        period = ReportPeriod.objects.filter(
                start_date = start_date,
                end_date = end_date)

        if len(period) == 0:
                
                ReportPeriod.objects.create(
                        start_date = start_date,
                        end_date = end_date)
                return ReportPeriod.objects.latest()
        else:
                return period[0]
                
       

def nested_fields(model, max_depth=2):
        
	def iterate(model, nest=None):
		fields = []
		
		# iterate all of the fields in this model, and recurse
		# each foreign key to include fields from nested models

                # For Each model, exculde unrequired fileds

                if model == Entry:
                        exculded_field_name = ["time"]
                        filtered_fields = [field for field in model._meta.fields if field.name not in exculded_field_name]
                        
                elif model == RUTFReporter or model == Reporter:
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
    

    table = context_dict['table']
    for column in table.columns:
        ws.write(0, c, column.name, header_style)
        c += 1

    r = 1
    for row in table.rows:
        style = normal_style
        c = 0
        for cell_value in row.data:
            #ws.write(r, c, unicode(cell_value), style)
            ws.write(r, c, unicode(row.data.get(cell_value)), style)
            c += 1
        r += 1

    temp_buffer = StringIO()
    wb.save(temp_buffer)
    return temp_buffer.getvalue()
