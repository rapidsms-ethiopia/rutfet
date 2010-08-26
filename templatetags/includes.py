#!/usr/bin/env python
# vim: noet

from datetime import datetime, timedelta
from rutfet.utils import *
import fpformat

from rutfet.models import *
from rutfet.scope import *

from django import template
register = template.Library()



@register.inclusion_tag("messages.html")
def incl_messages(type):
	
	if type == "in":
		capt = "Incoming"
		og = False
		
	elif type == "out":
		capt = "Outgoing"
		og = True
	
	return {
		"caption": "Recent %s Messages" % (capt),
		"messages": Message.objects.filter(is_outgoing=og).order_by("-time")[:10]
	}


@register.inclusion_tag("period.html")
def incl_reporting_period():
	start, end = current_reporting_period()
	return { "start": start, "end": end }

@register.inclusion_tag("report_filter.html", takes_context=True)
def incl_report_filter(context):
	from django.utils.text import capfirst
	from django.utils.html import escape
	from django.contrib import admin
	
	def no_auto_fields(field):
		from django.db import models
		return not isinstance(field[2], models.AutoField)
	
	models = []	
	for model, m_admin in admin.site._registry.items():
		
		# fetch ALL fields (including those nested via
		# foreign keys) for this model
		
		fields = [{ "caption": escape(capt), "name": name, "help_text": field.help_text }
			for name, capt, field in filter(no_auto_fields, nested_fields(model))]
		
		# pass model metadata and fields array
		# to the template to be rendered

		#select models only related to rutfet
		if model._meta.app_label == "rutfet":
                        models.append({
                                "caption": capfirst(model._meta.verbose_name_plural),
                                "name":    model.__name__.lower(),
                                "app_label": model._meta.app_label,
                                "fields": fields
                        })

        return {"models": models, "model_name":context["model_name"]}

