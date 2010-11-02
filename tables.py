
from .models import *

import django_tables as tables



class EntryTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    supply_place = tables.Column(verbose_name = 'OTP/Woreda Name')
    quantity = tables.Column(verbose_name = 'Quantity Received')
    consumption = tables.Column(verbose_name = 'Consumption')
    balance = tables.Column(verbose_name = 'balance')
    rutf_reporter = tables.Column(verbose_name = 'Reported By')


class ReporterEntryTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    period = tables.Column(verbose_name = 'Period')
    quantity = tables.Column(verbose_name = 'Quantity Received')
    consumption = tables.Column(verbose_name = 'Consumption')
    balance = tables.Column(verbose_name = 'balance')


class HealthPostEntryTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    period = tables.Column(verbose_name = 'Period')
    quantity = tables.Column(verbose_name = 'Quantity Received')
    consumption = tables.Column(verbose_name = 'Consumption')
    balance = tables.Column(verbose_name = 'balance')
    rutf_reporter = tables.Column(verbose_name = 'Reported By')

    

class AlertTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    notice = tables.Column(verbose_name = u"Alert Message")
    time = tables.Column(verbose_name = u"Time Sent")
    resolved = tables.Column(verbose_name = u"Resolved")
    #rutf_reporter = tables.Column(verbose_name = u"Reported By")
    
        
    
class SupplyTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    name = tables.Column(verbose_name = u"Supply Name")
    code = tables.Column(verbose_name = u"Supply Code")
    unit = tables.Column(verbose_name = u"Measurment Unit")

class RUTFReporterTable(tables.Table):
    reporter_id = tables.Column(verbose_name = "Reporter ID", visible=False)
    alias = tables.Column(verbose_name = "Username")
    first_name = tables.Column(verbose_name = "Name")
    last_name = tables.Column(verbose_name = "Father Name", visible= False)
    location = tables.Column(verbose_name = "Location")
    phone = tables.Column(verbose_name = "Phone Number")

    
class HealthPostTable(tables.Table):
    healthpost_id = tables.Column(verbose_name = 'Healthpost ID', visible=False)
    name = tables.Column(verbose_name = 'Name')
    code = tables.Column(verbose_name = 'Location Code', visible= False)
    #type = tables.Column(verbose_name = 'Type')
    woreda = tables.Column(verbose_name= 'Woreda')
    zone = tables.Column(verbose_name = 'Zone')
    reporter = tables.Column(verbose_name = "Reporter(s)")

    class Meta:
        per_page = 4


class WebUserTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    first_name = tables.Column(verbose_name = 'First Name')
    last_name = tables.Column(verbose_name = 'Last Name')
    username = tables.Column(verbose_name = 'Username')
    location = tables.Column(verbose_name = 'Place Assigned')
    #group = tables.Column()

#class SupplyPlaceTable(tables.Table):
#    pass
    
    
