from optparse import make_option

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from ui.models import TwitterUser, TwitterUserSet


class Command(BaseCommand):
    help = 'Add list of TwitterUsers from a text file, with one' \
           'TwitterUser name per line'

    option_list = BaseCommand.option_list + (
        make_option('--setname', action='store', default=False, dest='setname',
                    help='Add TwitterUsers to a TwitterUserSet'),
        )

    #help message will display [input-filepath] as a required arg
    @classmethod
    def usage(self, *args):
        usage = 'Usage: ./manage.py add_userlist [input-filepath] ' + \
                '[options]' + '\n' + self.help
        return usage

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Please specify one input file')
        userlist_file = open(args[0])
        # check if setname is present, if not create it
        set_name = options['setname']
        tuset_id = None
        if set_name:
            tusets_matching = TwitterUserSet.objects.filter(
                name__iexact=set_name)
            # if the set does not yet exist in SFM
            if len(tusets_matching) == 0:
                if raw_input('TwitterUserSet %s not found in SFM.' % set_name
                             + ' Create new set %s (Y/N)? ' %
                             set_name).upper() == 'Y':
                    try:
                        twitteruser = User.objects.get(
                            username=settings.TWITTER_DEFAULT_USERNAME)
                        tuset = TwitterUserSet(name=set_name,
                                               user_id=twitteruser.id)
                        tuset.save()
                        tuset_id = tuset.id
                    except Exception as e:
                        print 'Error creating set %s:' % set_name, e
                        return
                else:
                    return
            else:
                tuset_id = tusets_matching[0].id
                # re-get the name to correct any case inaccuracies
                set_name = tusets_matching[0].name
        #read the input file, add userlist and respective setname
        for tuser_name_raw in userlist_file:
            # skip blank lines
            if not tuser_name_raw.strip():
                continue
            tu_name = tuser_name_raw.lstrip().lstrip("@").rstrip()
            tu_matching = TwitterUser.objects.filter(name__iexact=tu_name)
            # if twitter user isn't already in SFM, add it.
            if len(tu_matching) == 0:
                try:
                    twitter_user = TwitterUser(name=tu_name)
                    twitter_user.clean()
                    twitter_user.save()
                    if set_name:
                        try:
                            twitter_user.sets.add(tuset_id)
                            print 'TwitterUser %s successfully added to ' \
                                'SFM and successfully added to ' \
                                'TwitterUserSet %s.' % (tu_name, set_name)
                        except Exception as e:
                            print 'TwitterUser %s successfully added to ' \
                                'SFM but unable to add to TwitterUserSet %s ' \
                                '-- Error: ' % (tu_name, set_name), e
                    else:
                        print 'TwitterUser %s successfully added to SFM.' \
                            % tu_name
                except Exception as e:
                    if 'not found' in e.message:
                        print '%s is not a valid Twitter user.  Not added ' \
                            'to SFM.' % tu_name
                    else:
                        print 'Unable to create TwitterUser %s in SFM ' \
                            '-- Error: ' % tu_name, e
            else:
                # if user exists, add to set if needed
                twitter_user = tu_matching[0]
                if set_name:
                    # check if the user already has the set
                    tu_sets_matching = twitter_user.sets.filter(id=tuset_id)
                    if len(tu_sets_matching) == 0:
                        try:
                            twitter_user.sets.add(tuset_id)
                            print 'TwitterUser %s found in SFM and ' \
                                  'successfully added to TwitterUserSet %s.' \
                                  % (tu_name, set_name)
                        except Exception as e:
                            print 'TwitterUser %s found in SFM, but ' \
                                  ' unable to add to TwitterUserSet %s ' \
                                  '-- Error: ' % (tu_name, set_name), e
                    else:
                        print 'TwitterUser %s is already in SFM and already ' \
                              'in TwitterUserSet %s.' % (tu_name, set_name)
                else:
                    print 'TwitterUser %s is already in SFM.' % tu_name
