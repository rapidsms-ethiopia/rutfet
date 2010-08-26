from django.conf.urls.defaults import *
import os
import rutfet.views as views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns("",
    
    # send sms
    #   (r'^send_sms/$', views.send_sms),

    # HEW registration form for Woreda Health officer
        (r'^rutf/register_HEW',views.register_hew),

    # report in tabular form
        (r'^rutf/reports', views.reports),

    # report in chart form
        (r'^rutf/charts', views.charts),
	
    # report in google maps view
	(r'^rutf/map/$', views.map_entries),

    # index page of rutf application  
        (r'^rutf/$', views.index),

    # Display detail information about the reporter
        (r'^rutf_reporter/(?P<id>\d+)/$', views.reporter_detail),

    # Display admin page
        (r'^admin/', include(admin.site.urls)),

                       
)

