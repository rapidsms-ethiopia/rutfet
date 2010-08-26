
from .models import *

import django_tables as tables



class EntryTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    supply_place = tables.Column(verbose_name = 'OTP/Woreda Name')
    quantity = tables.Column(verbose_name = 'Quantity Received')
    consumption = tables.Column(verbose_name = 'Consumption')
    balance = tables.Column(verbose_name = 'balance')
    rutf_reporter = tables.Column(verbose_name = 'Reported By')

    

class AlertTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    notice = tables.Column(verbose_name = u"Alert Message")
    resolved = tables.Column(verbose_name = u"Is Resolved")
    time = tables.Column(verbose_name = u"Time")
    rutf_reporter = tables.Column(verbose_name = u"Reported By")
    
        
    
class SupplyTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    name = tables.Column(verbose_name = u"Supply Name")
    code = tables.Column(verbose_name = u"Supply Code")
    unit = tables.Column(verbose_name = u"Measurment Unit")

class RUTFReporterTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    first_name = tables.Column(verbose_name = "Name")
    last_name = tables.Column(verbose_name = "Father Name")
    phone = tables.Column(verbose_name = "Phone Number")
    location = tables.Column(verbose_name = "Location")
    
class HealthPostTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    name = tables.Column(verbose_name = 'Name')
    code = tables.Column(verbose_name = 'Location Code')
    type = tables.Column(verbose_name = 'Type')
    child_number = tables.Column(verbose_name= 'Number of Child Location')
    parent_name = tables.Column(verbose_name = 'Parent Location')


class WebUserTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    first_name = tables.Column(verbose_name = 'First Name')
    last_name = tables.Column(verbose_name = 'Last Name')
    username = tables.Column(verbose_name = 'Username')
    location = tables.Column(verbose_name = 'Place Assigned')
    #group = tables.Column()

#class SupplyPlaceTable(tables.Table):
#    pass
    
    
