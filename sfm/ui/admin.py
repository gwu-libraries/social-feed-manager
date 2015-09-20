import os
from django.contrib import admin
from django.contrib import messages

import tweepy
from ui import models as m
from django.conf import settings


class TwitterFilterAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'user', 'is_active', 'words', 'people',
                    'locations']
    list_filter = ['is_active']
    search_fields = ['name', 'words', 'people', 'locations']
    fields = ('name', 'user', 'is_active', 'words', 'people', 'locations')

    def save_model(self, request, obj, form, change):
        ppl_submitted = []
        uids = []
        ppl_found = []
        ppl_not_found = []
        warn_msg = {'supervisor_not_running': False, 'tweep_error': False,
                    'invalid_acc': False}

        if obj.people.lstrip().rstrip():
            for person in obj.people.split(','):
                # create array of cleaned-up usernames
                ppl_submitted.append(person.lstrip().lstrip('@').rstrip())
        if ppl_submitted == []:
            obj.uids = ''
        else:
            try:
                print ppl_submitted
                api = m.authenticated_api(username=
                                          settings.TWITTER_DEFAULT_USERNAME)
                profiles_found = api.lookup_users(screen_names=ppl_submitted)
                # construct lower-case equivalent for usernames submitted
                for profile in profiles_found:
                    uids.append(profile['id'])
                    sn = str(profile['screen_name'])
                    ppl_found.append(sn)

                # set the filter's uids to a comma-separated list of uids
                # of found profiles
                obj.uids = ', '.join(map(str, uids))

                # create a lower-case version of ppl_found
                # for case-sensitive comparison of lists
                ppl_found_lower = set(n.lower() for n in ppl_found)

                # Compare lists, create list of people_not_found
                # (needed when we display the warning)
                for p in ppl_submitted:
                    if p.lower() not in ppl_found_lower:
                        ppl_not_found.append(p)
                # At least one account name wasn't found
                if ppl_not_found != []:
                    warn_msg['invalid_acc'] = True

                # save people list back to the model without @ symbols
                obj.people = ', '.join(ppl_submitted)

            except Exception as e:
                if tweepy.error.TweepError:
                    if e[0][0]['code'] == 17:
                        warn_msg['invalid_acc'] = True
                        ppl_not_found = ppl_submitted
                    else:
                        warn_msg['tweep_error'] = True
                        warn_msg['error'] = e[0][0]['message']

        if os.path.exists(settings.SUPERVISOR_UNIX_SOCKET_FILE) is False:
            warn_msg['supervisor_not_running'] = True
        if warn_msg['tweep_error']:
            messages.add_message(request, messages.WARNING,
                                 'TwitterFilter %s was saved with the '
                                 'exception: %s' % (obj.id, warn_msg['error']))
        if warn_msg['supervisor_not_running']:
            messages.add_message(request, messages.WARNING,
                                 'Supervsiord is not running, TwitterFilter %s'
                                 ' saved but not added to supervisor'
                                 ' subprocesses' % (obj.id))
        if warn_msg['invalid_acc']:
            messages.add_message(request, messages.WARNING,
                                 'TwitterFilter %s was saved with the'
                                 ' following invalid accounts: %s' %
                                 (obj.id, ', '.join(map(str, ppl_not_found))))

        super(TwitterFilterAdmin, self).save_model(request, obj, form, change)


admin.site.register(m.TwitterFilter, TwitterFilterAdmin)


class TwitterUserAdmin(admin.ModelAdmin):
    fields = ('name', 'is_active', 'uid', 'former_names', 'sets',
              'date_last_checked')
    list_display = ['id', 'is_active', 'uid', 'name', 'former_names',
                    'date_last_checked']
    list_filter = ['is_active']
    search_fields = ['name', 'former_names', 'uid']
    filter_horizontal = ['sets']

    def get_readonly_fields(self, request, obj=None):
        # if this is not a new object
        if obj:
            return ['uid', 'name', 'former_names', 'date_last_checked']
        else:
            return ['uid', 'former_names', 'date_last_checked']

admin.site.register(m.TwitterUser, TwitterUserAdmin)


class TwitterUserItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'twitter_user', 'date_published', 'twitter_id']
    list_filter = ['date_published']
    search_fields = ['twitter_id', 'item_text']
    readonly_fields = ['twitter_id', 'twitter_user', 'date_published',
                       'item_text', 'item_json', 'place', 'source']
admin.site.register(m.TwitterUserItem, TwitterUserItemAdmin)


class DurationSecondsFilter(admin.SimpleListFilter):
    title = 'duration (s)'
    parameter_name = 'duration_seconds'

    def lookups(self, request, model_admin):
        return (
            ('lt-0.25', '<= 0.25'),
            ('0.25-0.5', '0.25 - 0.5'),
            ('0.5-2', '0.5 - 2'),
            ('gt-2', '>= 2'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'lt-0.25':
            return queryset.filter(duration_seconds__lte=0.25)
        if self.value() == '0.25-0.5':
            return queryset.filter(duration_seconds__gt=0.25,
                                   duration_seconds__lte=0.5)
        if self.value() == '0.5-2':
            return queryset.filter(duration_seconds__gt=0.5,
                                   duration_seconds__lte=2)
        if self.value() == 'gt-2':
            return queryset.filter(duration_seconds__gt=2)


class TwitterUserItemUrlAdmin(admin.ModelAdmin):
    list_display = ['id', 'item', 'final_status', 'duration_seconds',
                    'expanded_url', 'final_url']
    list_filter = ['date_checked', 'final_status', DurationSecondsFilter]
    search_fields = ['id', 'start_url', 'expanded_url', 'final_url']
    readonly_fields = ['item']
admin.site.register(m.TwitterUserItemUrl, TwitterUserItemUrlAdmin)


class TwitterUserSetAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'notes']
    search_fields = ['user', 'name']
admin.site.register(m.TwitterUserSet, TwitterUserSetAdmin)


class TwitterUserTimelineJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'date_started', 'date_finished', 'num_added']
    list_filter = ['date_started']
    search_fields = ['id']
    readonly_fields = ['date_started', 'date_finished', 'num_added']
admin.site.register(m.TwitterUserTimelineJob, TwitterUserTimelineJobAdmin)


class TwitterUserTimelineErrorAdmin(admin.ModelAdmin):
    list_display = ['id', 'job', 'user', 'error']
    search_fields = ['job', 'user']
    readonly_fields = ['job', 'user', 'error']
admin.site.register(m.TwitterUserTimelineError, TwitterUserTimelineErrorAdmin)
