from datetime import datetime, timedelta
from django.utils.text import capfirst
from django.utils import translation
from models import *




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
                


def nested_fields(model, max_depth=4):
	def iterate(model, nest=None):
		fields = []
		
		# iterate all of the fields in this model, and recurse
		# each foreign key to include fields from nested models
		for field in model._meta.fields:
			if nest is None: my_nest = [field]
			else: my_nest = nest + [field]
			
			# is this a foreign key? (also abort if depth is too deep)
			if (hasattr(field, "rel")) and (field.rel is not None) and (len(my_nest) <= max_depth):
				fields.extend(iterate(field.rel.to, my_nest))
			
			# add the field object as a tuple, including the
			# caption (containing prefixes) and the class itself
			else:
				filter = "__".join([f.name for f in my_nest])
				label = "/".join([capfirst(translation.ungettext(f.verbose_name, "", 1)) for f in my_nest])
				fields.append((filter, label, field))
		
		return fields

	# start processing at the top
	return iterate(model)
