#!/usr/bin/env python
# vim: noet

SUPPORT = "UNICEF"
SORRY = "Sorry, I did not understand your message. "

ENGLISH = {
	"unknown_alias":  "I don't know anyone called %s",
	"unknown":        "The %s %s does not exist",
	"suggest":        "No such %s as %s. Did you mean %s (%s)?",
	"error":          SORRY + "For help, please reply: HELP",
	
	"ident":          "Hello, %s",
	"ident_again":    "Hello again, %s",
	"ident_help":     SORRY + "Please tell me who you are by replying: I AM YOUR-USERNAME",	
	
	"whoami":         "You are %s",
	"whoami_unknown": "I don't know who you are. Please tell me by replying: I AM YOUR-USERNAME",
	"whoami_help":    SORRY + "To find out who you are registered as, please reply: WHO AM I",
	
	"whois":          "%s is %s",
	"whois_help":     SORRY + "Please tell me who you are searching for, by replying: WHO IS USERNAME",

	"alert_ok":       "Thanks %s, Your alert was received and sent to Server",
	"alert_help":     SORRY + "Please tell me what you are alerting, by replying: ALERT YOUR-NOTICE",

        "activate_ok":     "You are set to active reporter. Now you can send report.",
        "activate_help":     SORRY + "To be active reporter, reply as: ACTIVATE",
	
	"cancel_ok":      "Thanks %s, your %s report has been cancelled",	
	"cancel_code_ok": "Your last report for the health post %s has been deleted. Please send the correct report before the deadline.",	
	#"cancel_none":    "You have not submitted any reports today, %s. If you wish to change an older entry, please call " + SUPPORT,
        "cancel_none":    "You have not submitted any report in the current period, or you have entered wrong place code.",
        "cancel_late":    "You are late to cancel a report.",
	"cancel_help":    SORRY + "You may delete your last report by replying: CANCEL LOCATION-CODE",
	
	"supplies_help":  SORRY + "To list all supply codes, please reply: SUPPLIES",
	
	"help_main":   "Help: reply with HELP ACTIVATE for activation, HELP REPORT for report formatting, or HELP ALERT for help with alerting",
	"help_help":   SORRY + "Please reply: HELP ACTIVATE, HELP REPORT or HELP ALERT",
	"help_report": "To make a report reply with: SUPPLY-CODE LOCATION-CODE QUANTITY CONSUMPTION BALANCE.",
	#"help_reg":  "If your mobile number is not registered, please reply: I AM YOUR-USERNAME",
        "help_reg":  "If your mobile number is not registered, please contact Health officer in the nearest woreda",
	"help_alert":  "To send alert, reply with ALERT followed by your notice",
        "help_cancel": "To cancel recent report, reply with CANCEL followed by location code.",
        "help_activate":  "To be active reporter, reply as: ACTIVATE or ACTIVATE ME",

	"conv_welc": "You're welcome, %s!",
	"conv_greet": "Greetings, friend!",
}

