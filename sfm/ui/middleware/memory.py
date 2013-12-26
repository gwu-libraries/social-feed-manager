import os
import psutil
import sys

THRESHOLD = 2*1024*1024


class MemoryUsageMiddleware(object):

    def process_request(self, request):
        request._mem = psutil.Process(os.getpid()).get_memory_info()

    def process_response(self, request, response):
        mem = psutil.Process(os.getpid()).get_memory_info()
        diff = mem.rss - request._mem.rss
        if diff > THRESHOLD:
            print('MEMORY USAGE = %r KB, path = %s' % (diff/1024, request.path))
        return response
