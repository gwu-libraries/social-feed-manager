#from django.conf import settings
from django.core.management.base import BaseCommand
import reversion
import datetime
from ui.models import TwitterUser


class Command(BaseCommand):
    help = 'revert the data for TwitterUser'

    def handle(self, *args, **options):
        deleted_list = reversion.get_deleted(TwitterUser)
        for item in deleted_list:
            value = str(item)
            print "the Deleted items are: %s" % value
            pk_value = value[len(value)-5:len(value)-1]
            pk_value = pk_value.lstrip("id").lstrip().rstrip()
            print int(pk_value)

        #old versions
        sfm_list = TwitterUser.objects.all()
        for item in iter(sfm_list):
            value = str(item)
            pk_value = value[len(value)-5:len(value)-1]
            pk_value = pk_value.lstrip("id").lstrip().rstrip()
            Twitter_User = TwitterUser.objects.get(pk=int(pk_value))
            version_list = reversion.get_for_object(Twitter_User)
            print version_list
            version = reversion.get_for_date(Twitter_User, datetime.datetime(2014, 5, 23))
            print version.field_dict
#            print version.revert()
#            if version_list[1] != 0:
#                print "the list of version list is: %s" % version_list
#3            else:
#                print " only one value"


'''

#        print datetime.datetime(2014, 5, 22)
#        version = reversion.get_for_date(Twitter_User, datetime.datetime(2014, 5, 22))
#        version_data = version.field_dict
        print version_list
#        print version_data
#        version = version_list[0]
#        print version.revert()
#        print version_data



#            delete_version = deleted_list.get(id=int(pk_value))
#            print delete_version.revision.revert()
#            print "version not present"
        #old versions
'''
