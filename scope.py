from models import *


class Scope:

        def __init__(self, location):
                self.is_global =  None
                self.location = location
                self.woreda_id = -1
                self.zone_id = -1
                self.region_id = -1

        def __unicode__(self):
                if self.location == None:
                        return u'All'
                else:
                        return self.location.name

        def woreda(self):
                if self.is_global:
                        return Location.objects.filter(type__name = 'woreda')
                else:
                        return filter(lambda loc: loc.type.name.lower() == 'woreda',
                                      self.location.ancestors(include_self=True))

        def set_woreda(self, woreda_id):
                self.woreda_id = woreda_id
                if woreda_id == -1:
                        self.location = None
                else:
                        try:
                                self.location = Location.objects.get(id = woreda_id)
                        except Location.DoesNotExist:
                                self.location = None

        def zone(self):
                if self.is_global:
                        return Location.objects.filter(type__name = 'zone')
                else:
                        return filter(lambda loc: loc.type.name.lower() == 'zone',
                                      self.location.ancestors(include_self=True))

        def set_zone(self, zone_id):
                self.zone_id = zone_id
                if zone_id == -1:
                        self.location = None
                else:
                        try:
                                self.location = Location.objects.get(id = zone_id)
                        except Location.DoesNotExist:
                                self.location = None

        def region(self):
                if self.is_global:
                        return Location.objects.filter(type__name = 'region')
                else:
                        return filter(lambda loc: loc.type.name.lower() == 'region',
                                      self.location.ancestors(include_self=True))

        def set_region(self, region_id):
                self.region_id = region_id
                if region_id == -1:
                        self.location = None
                else:
                        try:
                                self.location = Location.objects.get(id = region_id)
                        except Location.DoesNotExist:
                                self.location = None

        def health_posts(self):
                ''' Returns the health posts within the scope location '''
                if  self.location == None:
                        return HealthPost.objects.all()
                else:
                        return HealthPost.list_by_location(self.location)

        # only those HEWs form the the health post
        def rutf_reporters(self):
                ''' Return the reporters with health extension worker role
                within the scope location '''

                health_posts = self.health_posts()
                rutf_reporters = []
##                for rutf_reporter in RUTFReporter.objects.filter(role__code = 'hew'):
##                for rutf_reporter in RUTFReporter.objects.all():
                
                for rutf_reporter in RUTFReporter.objects.filter(role__code = 'hew'):
                        if HealthPost.by_location(rutf_reporter.location) in health_posts:
                                rutf_reporters.append(rutf_reporter)
                return rutf_reporters

        def alerts(self):
                ''' Return the Alerts which are reported by the health extension worker
                within the scope location'''
                rutf_reporters = self.rutf_reporters()
                alerts = []
                for alert in Alert.objects.all():
                        if alert.rutf_reporter in rutf_reporters:
                                alerts.append(alert)
                return alerts

##        def entries(self):
##                ''' Return the rutf entries which are reported by the
##                health extension worker within the scope location '''
##                rutf_reporters = self.rutf_reporters()
##                entries = []
##                for entry in Entry.objects.all():
##                        if entry.rutf_reporter in rutf_reporters:
##                                entries.append(entry)
##                return entries

        def entries(self):
                ''' Return the rutf entries which are reported
                from location in that is in the user's scope'''
                health_posts = self.health_posts()
                entries = []
                for entry in Entry.objects.all():
                        if entry.supply_place.location in health_posts:
                                entries.append(entry)
                return entries

        def web_user(self):
                ''' Return the rutf web_users who worker within the scope location '''
                health_posts = self.health_posts()
                web_users = []

                # you can specify the role of the web user
                for web_user in WebUser.objects.all():
                        if web_user.location in health_posts:
                                web_users.append(web_user)
                return web_users



def define_scope(f):
        ''' Defines the scope for any webuser '''

        def _inner(request, *args, **kwargs):
                webuser = WebUser.by_user(request.user)
                scope = Scope(webuser.location)
                if scope.is_global:
                        if request.method == 'POST' and 'woreda' in request.POST:
                                request.session['woreda'] = int(request.POST['woreda'])
                                scope.set_woreda(request.session.get('woreda',-1))
                                
                        elif request.method == 'POST' and 'zone' in request.POST:
                                request.session['zone'] = int(request.POST['zone'])
                                scope.set_zone(request.session.get('zone',-1))
                                
                        elif request.method == 'POST' and 'region' in request.POST:
                                request.session['region'] = int(request.POST['region'])
                                scope.set_region(request.session.get('region',-1))

                return f(request, scope, *args, **kwargs)
        return _inner

