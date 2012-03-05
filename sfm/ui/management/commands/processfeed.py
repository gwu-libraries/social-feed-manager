import gzip 
from optparse import make_option
import os
import shutil
from StringIO import StringIO
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import simplejson as json

from lxml import etree

from ui.models import Status

NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'gnip': 'http://www.gnip.com/schemas/2010',
    'activity': 'http://activitystrea.ms/spec/1.0/',
    }

class Command(BaseCommand):
    help = 'Process files into the database'
    option_list = BaseCommand.option_list + (
        make_option('--move', action='store_true', default=False,
            dest='move', help='move processed files aside'),
        make_option('--dir', action='store', type='string',
            default=settings.DATA_DIR, dest='dir',
            help='directory containing unprocessed data (default=DATA_DIR)'),
        )

    def handle(self, *args, **options):
        unprocessed_files = [f for f in os.listdir(options['dir']) \
            if f.endswith('xml.gz')]
        for unprocessed_file in unprocessed_files:
            print 'processing:', unprocessed_file
            filename = '%s/%s' % (options['dir'], unprocessed_file)
            try:
                self._process_file(filename)
            except IOError:
                print '*******'
                print 'IOError:', filename
                print '*******'
                continue
            if options.get('move', False):
                print 'moving file aside'
                target_filename = '%s/processed/%s' % (options['dir'],
                    unprocessed_file)
                print 'shutil.move("%s", "%s")' % (filename, target_filename)
                shutil.move(filename, target_filename)

    def _process_file(self, filename):
        fp = gzip.open(filename, 'rb')
        entry = []
        for line in fp:
            entry.append(line)
            if '</entry>' in line:
                self._parse_entry(''.join(entry)) 
                entry = []
        fp.close()

    def _parse_entry(self, entry):
        parser = etree.XMLParser(no_network=True, resolve_entities=False)
        r = etree.parse(StringIO(entry))
        # published
        e_published = r.find('//{%s}published' % NS['atom'])
        #date_published = time.strptime(e_published.text,
        #    '%Y-%m-%dT%H:%M:%SZ')
        # FIXME: don't be punting on timezone differences now
        date_published = e_published.text.replace('T', ' ')
        date_published = date_published.replace('Z', '')
        # userid
        e_author = r.find('//{%s}author' % NS['activity'])
        author_link = e_author.find('.//{%s}id' % NS['atom']).text
        # avatar url
        author_avatar = e_author.find('.//{%s}link[@rel="avatar"]' % NS['atom']).attrib['href']
        # status id
        status_link = r.find('./{%s}link' % NS['atom']).attrib['href']
        # summary / content?
        summary = r.find('./{%s}summary' % NS['atom']).text
        content = r.find('.//{%s}content' % NS['atom']).text
        # urls long/short
        # matching rule source/inferred tag / value
        e_rule = r.find('//{%s}matching_rule[@rel="source"]' % NS['gnip'])
        rule = {
            'rel': e_rule.attrib['rel'],
            'tag': e_rule.attrib['tag'],
            'value': e_rule.text,
            }
        status, created = Status.objects.get_or_create(
            user_id=author_link, date_published=date_published,
            avatar_url=author_avatar, status_id=status_link,
            summary=summary, content=content,
            rule_tag=rule['tag'], rule_match=rule['value'])
        if created:
            print 'saved:', status_link
        else:
            print 'skip:', status_link


# NOTE: json url pattern for a single tweet is:
# http://api.twitter.com/1/statuses/show/176547251324329984.json
