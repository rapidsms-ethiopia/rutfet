
import djtables as tables


class EntryTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    supply_place = tables.Column(name = u"OTP/Woreda Name")
    quantity = tables.Column(name = u"Quantity Received")
    consumption = tables.Column(name = u"Consumption")
    balance = tables.Column(name = u"Balance")
    rutf_reporter = tables.Column(name = u"Reported By")


class AlertTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    notice = tables.Column(name = u"Alert Message")
    resolved = tables.Column(name = u"Is Resolved")
    time = tables.Column(name = u"Time")
    rutf_reporter = tables.Column(name = u"Reported By")
    
class SupplyTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    name = tables.Column(name = u"Supply Name")
    code = tables.Column(name = u"Supply Code")
    unit = tables.Column(name = u"Measurment Unit")

class RUTFReporterTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    first_name = tables.Column(name = u"Name")
    last_name = tables.Column(name = u"Father Name")
    phone = tables.Column(name = u"Phone Number")
    location = tables.Column(name = u"Location")
    
class HealthPostTable(tables.Table):
    #pk = tables.Column(visible=False, sortable=False)
    name = tables.Column(name = u"Name")
    code = tables.Column(name = u"Code")
    type = tables.Column(name = u"Type")
    child_number = tables.Column(name = u"Number of Child Locations")
    parent_name = tables.Column(name = u"Parent Location Name")

#class WebUserTable(tables.Table):
#    pass

#class SupplyPlaceTable(tables.Table):
#    pass
    
    
