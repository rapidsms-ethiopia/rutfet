from django.conf.urls.defaults import *
##from export import views as ex_views
import os
import rutfet.views as views

urlpatterns = patterns("",
##    (r'^assets/(?P<path>.*)$', "django.views.static.serve",
##        {"document_root": os.path.dirname(__file__) + "/static"}),
##
##    (r'^graphs/(?P<path>.*)$', "django.views.static.serve",
##        {"document_root": os.path.dirname(__file__) + "/graphs"}),
##    
##	    
##    # exporting is magic!
##	(r'^(?P<app_label>.+?)/(?P<model_name>.+?)/export/excel/$', ex_views.to_excel),
##	(r'^(?P<app_label>.+?)/(?P<model_name>.+?)/export/print/$', views.to_print),
##	(r'^export/$', ex_views.export),
     
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
)

