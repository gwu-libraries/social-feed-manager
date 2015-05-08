import json
from optparse import make_option
import sys
from socket import error as socket_error
import codecs
import unicodedata

import requests

from django.core.management.base import BaseCommand, CommandError

from ui.models import TwitterUser, TwitterUserItem, TwitterUserItemUrl
from ui.utils import make_date_aware

from queryset_iterator import queryset_iterator


class Command(BaseCommand):
    help = 'fetch expanded urls for tweets with urls in text'

    option_list = BaseCommand.option_list + (
        make_option('--start-date', action='store', default=None,
                    type='string', dest='start_date',
                    help='earliest date (YYYY-MM-DD) for export'),
        make_option('--end-date', action='store', default=None,
                    type='string', dest='end_date',
                    help='latest date (YYYY-MM-DD) for export'),
        make_option('--twitter-user', action='store', default=None,
                    type='string', dest='twitter_user',
                    help='username to export'),
        make_option('--limit', action='store', default=0,
                    type='int', dest='limit',
                    help='max number of links to check'),
        make_option('--refetch', action='store_true', default=False,
                    help='refetch urls that have been fetched before'),
    )

    def handle(self, *args, **options):
        twitter_user = None
        start_dt = None
        end_dt = None
        if options['twitter_user']:
            try:
                twitter_user = TwitterUser.objects.get(
                    name=options['twitter_user'])
            except TwitterUser.DoesNotExist:
                raise CommandError('TwitterUser %s does not exist' %
                                   options['twitter_user'])

        if options['start_date']:
            start_dt = make_date_aware(options['start_date'])
            if not start_dt:
                raise CommandError('dates must be in the format YYYY-MM-DD')
        else:
            start_dt = None
        if options['end_date']:
            end_dt = make_date_aware(options['end_date'])
            if not end_dt:
                raise CommandError('dates must be in the format YYYY-MM-DD')
        else:
            end_dt = None
        if start_dt and end_dt:
            if end_dt < start_dt:
                raise CommandError('start date must be earlier than end date')

        if twitter_user:
            qs = twitter_user.items.all()
        else:
            qs = TwitterUserItem.objects.all()

        if not options['refetch']:
            qs = qs.filter(urls__isnull=True)

        if start_dt:
            qs = qs.filter(date_published__gte=start_dt)
        if end_dt:
            qs = qs.filter(date_published__lte=end_dt)

        qs = queryset_iterator(qs)

        count = 0
        for tui in qs:
            urls = []
            urls.extend(tui.tweet['entities']['urls'])
            if 'media' in tui.tweet['entities'].keys():
                urls.extend(tui.tweet['entities']['media'])
            if not urls:
                # use of entities.urls was spotty at first
                for u in tui.links:
                    if ('...' in unicodedata.normalize('NFKD', u).encode('ascii','ignore')
                        and tui.tweet['retweet_count'] > 0) :
                        continue
                    urls.append({'url': u, 'expanded_url': u})
            for url in urls:
                try:
                    r = requests.head(url['expanded_url'],
                                              allow_redirects=True,
                                              timeout=10)
                    if r.status_code == 405:
                        r = requests.get(url['expanded_url'],
                                                  allow_redirects=True,
                                                  stream=True, timeout=10)
                        r.close()
                    req_history_headers = []
                    for req in r.history:
                        req_headers = self.decode_headers(req.headers, req.encoding)

                        req_history_headers.append((
                            req.status_code,
                            req.url,
                            req_headers))

                    final_req_headers = self.decode_headers(r.headers, r.encoding)

                    tuiu = TwitterUserItemUrl(
                        item=tui,
                        start_url=url['url'],
                        expanded_url=url['expanded_url'],
                        history=json.dumps(req_history_headers),
                        final_url=r.url,
                        final_status=r.status_code,
                        final_headers=json.dumps(final_req_headers),
                        duration_seconds=r.elapsed.total_seconds())
                    tuiu.save()
                except (requests.RequestException) as e:
                    # TODO: consider trapping/recording
                    # requests.exceptions.ConnectionError,
                    # requests.exceptions.TooManyRedirects etc.
                    # and flagging records as having errored out
                    print("Request Exceptions Error fetching %s: %s" % (url['expanded_url'].encode('utf-8'), e))
                except (requests.packages.urllib3.exceptions.HTTPError) as e:
                    print("HTTPError fetching %s: %s" % (url['expanded_url'].encode('utf-8'), e))
                except (socket_error) as e:
                    print("Socket error fetching %s: %s" % (url['expanded_url'].encode('utf-8'), e))

                    tuiu = TwitterUserItemUrl(
                        item=tui,
                        start_url=url['url'],
                        expanded_url=url['expanded_url'],
                        final_url=url['url'],
                        final_status=410)
                    tuiu.save()

            if urls:
                count += 1
            if options['limit']:
                if count >= options['limit']:
                    sys.exit()

    def decode_headers(self, headers, encoding):
        try:
            header_codec = codecs.lookup(encoding
                                            or 'utf-8')
        except LookupError:
            header_codec = codecs.lookup('utf-8')

        final_headers = {}
        for k, v in headers.items():
            final_headers.update({
                header_codec.decode(k),
                header_codec.decode(v)})
        return final_headers
