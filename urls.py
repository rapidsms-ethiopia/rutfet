from django.conf.urls.defaults import *
import os
import rutfet.views as views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns("",

    # Dashboard
        (r'^$', views.index),
    

    # index page of rutf application  
        (r'^rutf/$', views.index),

    # report in tabular form
        (r'^rutf/reports/$', views.reports),

    # filter report tabular
        (r'^rutf/filter_reports/$', views.filter_reports),

    # report in chart form
        (r'^rutf/charts/$', views.charts),
	
    # report in maps view
	(r'^rutf/map/$', views.map_entries),
                       
    # send sms
    #   (r'^rutf/send_sms/$', views.send_sms),

    # Reporters
        (r'^rutf/reporters/$', views.reporters),

    # Healthposts
        (r'^rutf/health_posts/$', views.healthposts),

    # Healthpost detail
        (r'^rutf/health_post/(?P<healthpost_id>\d+)/$', views.healthpost),
                       
    # Display detail information about the reporter
        (r'^rutf/reporter/(?P<reporter_id>\d+)/$', views.reporter),

    # Send SMS message to reporters 
        (r'^rutf/send_sms/(?P<reporter_id>\d+)/$', views.send_sms),

    # Send SMS message to reporters 
        (r'^rutf/send_sms/$', views.send_sms),

    # Interemediate page to confirm confirmation of Reports :)
    #(r'^admin/confirmation/$', views.alert_detail),

    # Display admin page
        #(r'^admin/$', include(admin.site.urls)),

                       
)

