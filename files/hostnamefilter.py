import logging, platform

class HostnameFilter(logging.Filter):
    hostname = platform.node()
    def filter(self, record):
        record.hostname = HostnameFilter.hostname
        return True