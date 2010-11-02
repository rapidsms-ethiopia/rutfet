import rapidsms
import re
from datetime import date, datetime
from strings import ENGLISH as STR

from django.core.management import setup_environ
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rapidsms.apps.base import AppBase
from parsers.keyworder import * 
from models import *
from utils import *


class App (AppBase):
    # lets use the Keyworder parser!
    kw = Keyworder()

    # non-standard regex chunks
    ALIAS = '([a-z\.]+)'

    # Supply code list for Reporting
    supply_code_list = []
    for supply_code in Supply.objects.values_list("code"):
        supply_code_list.append(supply_code[0])

    supply_code_str = "|".join(supply_code_list)

    
    def __get(self, model, **kwargs):
        try:
            # attempt to fetch the object
	    return model.objects.get(**kwargs)
		
	# no objects or multiple objects found (in the latter case,
	# something is probably broken, so perhaps we should warn)
	except (ObjectDoesNotExist, MultipleObjectsReturned):
        	return None

    def __get_reporter(self, phone):
        try:
            # attempt to fetch the object
            reporters = []
            for reporter in RUTFReporter.objects.all():
                if reporter.phone == phone:
                    reporters.append(reporter)

            if len(reporters) > 0:
                return reporters[0]
            else:
                return None
		
	# no objects or multiple objects found (in the latter case,
	# something is probably broken, so perhaps we should warn)
	except (ObjectDoesNotExist, MultipleObjectsReturned):
        	return None
            
            
    def __identify(self, message, task=None):
        caller = message.connection.identity
        rutf_reporter = self.__get_reporter(phone=caller)
		
	# if the caller is not identified, then send
	# them a message asking them to do so, and
	# stop further processing
	if not rutf_reporter:
            msg = "Your phone is not registered. Please contact your supervisor"
            if task: msg += " before %s." % (task)
            #msg += ", by replying: I AM <USERNAME>"
            message.respond(msg)
            self.handled = True
		
	return rutf_reporter


    def __monitor(self,message, user_name):
	# some people like to include dots
	# in the username (like "a.mckaig"),
	# so we'll merrily ignore those
	clean = user_name.replace(".", "")
		
	# attempt to fetch the rutf_reporter from db
	# (for now, only by their user_name...
	rutf_reporter = self.__get(RUTFReporter, user_name=clean)
		
	# abort if nothing was found
	if not rutf_reporter:
        	message.respond(STR["unknown_name"] % user_name)
		
	return rutf_reporter
		    
    def __guess(self, string, within):
	try:
            from Levenshtein import distance
            import operator
            d = []
		
	# something went wrong (probably
	# missing the Levenshtein library)
	except:
            self.log("Couldn't import Levenshtein library", "warn")
            return None
		
	# searches are case insensitive
	string = string.upper()
		
	# calculate the levenshtein distance
	# between each object and the argument
	for obj in within:
		
            # some objects may have a variety of
            # ways of being recognized (code or name)
            if hasattr(obj, "guess"): tries = obj.guess()
            else: tries = [str(obj)]
			
            # calculate the intersection of
            # all objects and their "tries"
            for t in tries:
		dist = distance(str(t).upper(), string)
                d.append((t, obj, dist))
		
	    # sort it, and return the closest match
            d.sort(None, operator.itemgetter(2))
            if (len(d) > 0):# and (d[0][1] < 3):
		return d[0]
		
            # nothing was close enough
            else: return None


    def start (self):
        """Configure your app in the start phase."""
        #while True:
        #    print "waiting"
        pass

    def parse (self, message):
        self.handled = False

    def handle (self, message):

        self.handled = False
        try:
            if hasattr(self,"kw"):
                self.debug("HANDLE")
                
                # attempt to match tokens in this message
                # using the keyworder parser
                results = self.kw.match(self, message.text)
                if results:
                    func, captures = results
                    print func
                    # if a function was returned, then a this message
                    # matches the handler _func_. call it, and short-
                    # circuit further handler calls
                    func(self, message, *captures)
                    return self.handled
                else:
                    self.debug("NO MATCH FOR %s" % message.text)
            else:
                self.debug("App does not instantiate keyworder as 'kw'")
                
        except Exception, e:
            self.log_last_exception()
       

    def cleanup (self, message):
        """Perform any clean up after all handlers have run in the
           cleanup phase."""
        pass

    def outgoing (self, message):
        """Handle outgoing message notifications."""
        pass

    def stop (self):
        """Perform global app cleanup when the application is stopped."""
        pass


    
    # ALERT <NOTICE> ----------------------------------------------------------
    #kw.prefix = "[\"'\s]* alert [\.,\"'\s]*"

    @kw("[\"'\s]*alert[\"'\s]*(whatever)")
    def alert(self, message, notice):
        caller = message.connection.identity
        rutf_reporter = self.__identify(message,"alerting")
        if rutf_reporter is not None:
            Alert.objects.create(rutf_reporter=rutf_reporter, resolved=0, notice=notice)
            message.respond(STR["alert_ok"] % ("%s %s" % (rutf_reporter.first_name, rutf_reporter.last_name)))

    @kw.blank()
    @kw(r"\s+")
    def alert_help(self, message, *msg):
        message.respond(STR["alert_help"])



    # CANCEL ------------------------------------------------------------------
    kw.prefix = ["[\"'\s]*cancel", "[\"'\s]*cancle"]

    @kw("[\"'\s]*(letters)[\"'\s]*")
    def cancel_code(self, message, code):
        caller = message.connection.identity
        rutf_reporter = self.__identify(message, "cancelling")

        try:
            # attempt to find rutf_reporter's 
            # entry with this code in the current period

            month, year, late , dates_gc = current_reporting_period()
            period = get_or_generate_reporting_period()
            entry = Entry.objects.filter(
                    #rutf_reporter=rutf_reporter,\
                    report_period = period,\
                    supply_place__location__code=code)\
                    .order_by('-time')[0]
            
            if (late == True or entry.late == True) and rutf_reporter:
                message.respond("You can't cancel the report. It has been reported late.\
                                Or it is late to cancel the report")
            elif rutf_reporter:
                # delete it and notify
                previous_reporter = entry.rutf_reporter
                if rutf_reporter == previous_reporter:
                    entry.delete()
                    healthpost_name = HealthPost.objects.get(code = code).name
                    message.respond(STR["cancel_code_ok"] % (healthpost_name))
                else:
                    message.respond("You can not cancel the report. \
                        The report is sent by %s %s" % (previous_reporter.first_name, previous_reporter.last_name) )

        except (ObjectDoesNotExist, IndexError):
            if late == False:
                message.respond(STR["cancel_none"])
            else:
                message.respond(STR["cancel_late"])

    @kw.invalid()
    @kw.blank()
    def cancel_help(self, message, *msg):
        message.respond(STR["cancel_help"])

    
    
    
    # SUPPLIES ----------------------------------------------------------------
    kw.prefix = ["[\"'\s]*supplies[\"'\s]*", "[\"'\s]*supplys[\"'\s]*", "[\"'\s]*supply[\"'\s]*", "[\"'\s]*sups[\"'\s]*"]
    @kw.blank()
    def supplies(self, message):
        caller = message.connection.identity
        rutf_reporter = self.__identify(message,"requesting supplies")

        if rutf_reporter is not None:
            supplies = Supply.objects.all()
            supply_name_code = ["%s (%s)" % (supply.name, supply.code) for supply in supplies]
            supplylist = ", ".join(supply_name_code)
            message.respond(supplylist)
    
    @kw.invalid()
    def supplies_help(self, message):
        message.respond(STR["supplies_help"])


    # set me active reporter ------------------------------------------------
    
    kw.prefix = ["[\"'\s]*activate[\"'\s]*", "[\"'\s]*activate [\"'\s]*me[\"'\s]*",
        "[\"'\s]*active[\"'\s]*", "[\"'\s]*set [\"'\s]*active[\"'\s]*"]
    @kw.blank()
    def activate_reporter(self, message):
        caller = message.connection.identity
        rutf_reporter = self.__identify(message,"Activating")
        if rutf_reporter is not None and rutf_reporter.has_phone == True:
            # set other reporters in that location as inactive
            place_assigned = rutf_reporter.place_assigned
            reporters = place_assigned.reporters
            for reporter in reporters:
                if reporter == rutf_reporter:
                    rutf_reporter.is_active_reporter = True
                    rutf_reporter.save()
                    message.respond(STR["activate_ok"])
                else:
                    reporter.is_active_reporter = False
                    reporter.save()
                    
    @kw.invalid()
    def activate_help(self, message, *msg):
        message.respond(STR["activate_help"])
    

    
    # HELP <QUERY> ------------------------------------------------------------
    kw.prefix = ["help", "help me"]
    @kw.blank()
    def help_main(self, message):
        message.respond(STR["help_main"])
    
    @kw("report", "format", "fields")
    def help_report(self, message):
        message.respond(STR["help_report"])
    
    @kw("register", "identify")
    def help_report(self, message):
        message.respond(STR["help_reg"])
    
    @kw("alert")
    def help_report(self, message):
        message.respond(STR["help_alert"])

    @kw("cancel", "cancle")
    def help_report(self, message):
        message.respond(STR["help_cancel"])

    @kw("activate", "activate me", "active")
    def help_report(self, message):
        message.respond(STR["help_activate"])
    
    @kw.invalid()
    def help_help(self, message, *msg):
        message.respond(STR["help_help"])

    
    # CONVERSATIONAL  ------------------------------------------------------------
##    kw.prefix = ["ok", "thanks", "thank you"]
##    
##    @kw.blank()
##    @kw("(whatever)")
##    @kw.invalid()
##    def conv_welc(self, message):
##        caller = message.connection.identity
##        rutf_reporter = self.__identify(message, "thanking")
##        message.respond(STR["conv_welc"] % (rutf_reporter))
##        self.handled = True
##    
##
##
##    kw.prefix = ["hi", "hello", "whats up"]
##
##    @kw.blank()
##    @kw("(whatever)")
##    @kw.invalid()
##    def conv_greet(self, message, whatever=None):
##        caller = message.connection.identity
##        rutf_reporter = self.__get(rutf_reporter, phone=caller)
##        if rutf_reporter.phone == caller:
##            message.respond(STR["ident"] % (rutf_reporter))
##        message.respond(STR["conv_greet"])
##        self.handled = True

    
    

    # <SUPPLY> <PLACE> <QUANTITY> <CONSUMPTION> <BALANCE> --
    kw.prefix = ""
             
##    @kw("[\"'\s]*(letters)[,\.\s]*(\w+)(?:[,\.\s]*(\d+))?(?:[,\.\s]*(\d+))?(?:[,\.\s]*(\d+))?[\.,\"'\s]*")

    #@kw("[\"'\s]*(" + supply_code_str + ")[,\.\s]*(\w+)(?:[,\.\s]*(\d+))?(?:[,\.\s]*(\d+))?(?:[,\.\s]*(\d+))?[\.,\"'\s]*")
    
    @kw("[\"'\s]*(" + supply_code_str + ")[,\.\s]+(\w+)(?:[,\.\s]+(\d+))(?:[,\.\s]+(\d+))(?:[,\.\s]+(\d+))[\.,\"'\s]*")
    def report(self, message, supply_code, place_code, qty="", con="", bal=""):
        
        # ensure that the caller is known
        caller = message.connection.identity
        rutf_reporter = self.__identify(message, "reporting")
                
        
        # validate + fetch the supply
        sup_code = supply_code.upper()
        supply = self.__get(Supply, code=sup_code)
        
        if supply is None:
            message.respond(STR["unknown"]\
            % ("supply code", sup_code))
            self.handled = True

        plc_code = place_code.upper()
        # the "place" can be Health post, woreda, or zone
        place = self.__get(HealthPost, code=plc_code)

##        if place is None:
##            message.respond(STR["unknown"]\
##            % ("place code", plc_code))
##            self.handled = True

        month, year, late , dates_gc = current_reporting_period()            
        
        if rutf_reporter and supply and place and rutf_reporter.location == place and rutf_reporter.is_active_reporter == True:
                        
            # init variables to avoid
            # pythonic complaints
            health_post = None
            woreda = None
            zone = None
            
                    
            # fetch the supplylocation object, to update the current stock
            # levels. if it doesn't already exist, just create it, because
            # the administrators probably won't want to add them all...
            sp, created = SupplyPlace.objects.get_or_create(supply=supply, location=place)
            
            # create the entry object, 
            # unless its a duplicate report in the period
                        
            period = get_or_generate_reporting_period()
            month_year = "%s-%s" % (month, year)
            try:
                entry = Entry.objects.filter(
                        #rutf_reporter=rutf_reporter,
                        supply_place=sp,
                        report_period = period)\
                        .order_by('-time')[0]



                # if the reporter reports in the given period
                # inform the reporter that he has sumbitted report again

                if entry is not None:
                    # or Delete the old one and insert the new report
    ##                period = get_or_generate_reporting_period()
    ##                entry.delete()
    ##                Entry.objects.create(
    ##                    rutf_reporter=rutf_reporter,
    ##                    supply_place=sp,
    ##                    quantity=qty,
    ##                    consumption=con,
    ##                    balance=bal,
    ##                    report_period = period)

                    # Inform the reporter
                    if late == False:
                        previous_reporter_name = "%s %s" % (entry.rutf_reporter.first_name,entry.rutf_reporter.last_name)
                        current_reporter_name = "%s %s" % (rutf_reporter.first_name,rutf_reporter.last_name)

                        if previous_reporter_name == current_reporter_name:
                            message.respond("You have already reported for %s Month. \
                                        If that was not correct, reply with CANCEL %s."
                                        % (month_year, place.code))
                        else:
                            message.respond("%s have already reported for %s Month.\
                                            The previous report should be canceled first."
                                        % (previous_reporter_name, month_year))
                            
                    else:
                        previous_reporter_name = "%s %s" % (entry.rutf_reporter.first_name,entry.rutf_reporter.last_name)
                        current_reporter_name = "%s %s" % (rutf_reporter.first_name,rutf_reporter.last_name)
                        if previous_reporter_name == current_reporter_name:
                            message.respond("You have already reported for %s Month. \
                                        But now you are late to correct the previous report."
                                        % (month_year))
                        else:
                            message.respond("%s have already reported for %s Month. \
                                        But now you are late to correct the previous report."
                                        % (previous_reporter_name,month_year))
                    

            # If duplicate entry doesn't exist in the period
            except (ObjectDoesNotExist, IndexError):

                hp_allowed_late = False
                try:
                    LateHealthPost.objects.get(location = place, accept_late_report = True)
                    hp_allowed_late = True
                except Exception, e:
                    print e
                    
                # add the entry
                # Get the reporting period

                if late == False or hp_allowed_late:
                    Entry.objects.create(
                            rutf_reporter=rutf_reporter,
                            supply_place=sp,
                            quantity=qty,
                            consumption=con,
                            balance=bal,
                            report_period = period,
                            late = late)
                
                    # collate all of the information submitted, to
                    # be sent back and checked by the reporter
                    info = [
                            "qty=%s" % (qty or "??"),
                            "con=%s" % (con or "??"),
                            "bal=%s" % (bal or "??")]
                    
                    # notify the reporter of their new entry
                    #if place is not None:
                    last_report = Entry.objects.filter(
                            rutf_reporter=rutf_reporter,
                            supply_place=sp,
                            quantity=qty,
                            consumption=con,
                            report_period = period,
                            balance=bal)[0]
                        

                    # Generate receipt
                    new_receipt = last_report.new_receipt
                    # then update the receipt value of the report
                    last_report.receipt = new_receipt
                    last_report.save()
                    
                    message.respond(
                            "Received %s report for %s %s by %s: %s.If this is not correct, reply with CANCEL %s. Receipt Number = %s" %\
                            (supply.name, sp.type, sp.place.name, rutf_reporter, ", ".join(info), place.code ,new_receipt))
                else:
                    message.respond("You can not send your report. you are late.")
        else:
            if late == True and rutf_reporter:
                message.respond("You can not send your report. you are late.")                
                
            elif rutf_reporter:
                if rutf_reporter.is_active_reporter == True:
                    reporter_location_code = rutf_reporter.location.code
                    message.respond("You can not send your report. \
                        please check the supply code and the location code. \
                        Your location code is: %s" % reporter_location_code)
                else:
                    message.respond("Currently you are not active reporter. \
                        To activate yourself, please reply as: ACTIVATE")
                    
        
        
    @kw.invalid()
    def help_report(self, message, *msg):
        caller = message.connection.identity
        rutf_reporter = self.__identify(message, "reporting")

        if rutf_reporter:
            message.respond(STR["help_report"])

