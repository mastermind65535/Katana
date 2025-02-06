from threading import Thread
import requests
import dns.resolver
import logging
import time
import os
from logger import LOGGER
from Engine import RateLimit

LOG = LOGGER

class DNS_Engine:
    def __init__(self):
        pass

    def lookup(self, domain:str):
        try:
            time.sleep(RateLimit().getRate())
            dns.resolver.resolve(domain, "A")
            return True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.LifetimeTimeout):
            return False