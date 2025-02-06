import requests
import urllib
import logging
import traceback
import os
import sys
import socks
import socket

# Rate Limits
from Engine import RateLimit

# Common Exploit Payloads
from Engine.Payloads import SQLi
from Engine.Payloads import XSS
from Engine.Payloads import CSRF

# Application Protocols
from Engine.Protocols import DNS as DNS_Engine

# Database
from Engine.DB import subdomains_db

# Logger
from logger import LOGGER

LOG = LOGGER
ORIGIN_SOCKET = socket.socket
Local_Version = "2.0.0"
settings = {}

class Setting:
    def __init__(self):
        self.Settings = {
            "dns.subdomains.proto": "",
        }
        self.run()
    def run(self):
        for setting in self.Settings:
            settings[setting] = self.Settings[setting]

class Shell:
    class rate:
        def set(*args):
            if len(args) > 0 and args[0] == "help":
                return ['''Set ratelimits for sending data''', ["RATELIMIT"]]
            try:
                rate = float(args[0])
                RateLimit().setRate(rate)
            except:
                raise
        
        def print(*args):
            if len(args) > 0 and args[0] == "help":
                return ['''Print ratelimits for sending data''', ["N/A"]]
            try:
                print(f"Current Rate Limits: request/{RateLimit().getRate()}s")
            except:
                raise

        def calc(*args):
            if len(args) > 0 and args[0] == "help":
                return ['''Calculate ratelimit''', ["PKT/SECOND"]]
            try:
                data_amount = float(str(args[0]).split("/")[0])
                second = float(str(args[0]).split("/")[1])
                print(f"Calculated Rate Limits: request/{data_amount / second}s")
            except:
                raise

    class dns:
        def scope(*args):
            if len(args) > 0 and args[0] == "help":
                return ['''Scan subdomains''', ["DOMAIN"]]
            try:
                DOMAIN = str(args[0])
                found = []
                scanned = 0
                for subdomain in subdomains_db.SUBDOMAIN_STRING:
                    try:
                        url = f"{settings["dns.subdomains.proto"]}{subdomain}.{DOMAIN}"
                        Engine = DNS_Engine.DNS_Engine()
                        if (Engine.lookup(url) == True):
                            found.append(url)
                        scanned+= 1
                        LOG.debug(f"[+] Scanning... {url:<60}[FOUND: {len(found)} SCANNED: {scanned}]{' ' * 30}")
                    except KeyboardInterrupt:
                        break
                    
                LOG.debug(' ' * 100)
                LOG.debug(f"{'*' * 30}[SUBDOMAINS]{'*' * 30}")

                for found_domain in found:
                    LOG.info(found_domain)
            except:
                raise

    class proxy:
        def set(*args):
            if len(args) > 0 and args[0] == "help":
                return ['''Set proxy server''', ["SERVER", "PORT"]]
            try:
                PROXY_HOST = str(args[0])
                PROXY_PORT = int(args[1])
                socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, PROXY_HOST, PROXY_PORT, rdns=True)
                socket.socket = socks.socksocket
                
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("ifconfig.me", 80))
                s.sendall(b"GET / HTTP/1.1\r\nHost: ifconfig.me\r\nConnection: close\r\n\r\n")
                response = s.recv(4096).decode()
                s.close()

                ipv4_address = response.split("\r\n\r\n")[1].strip()
                LOG.info(f"Your IP address is (SOCKET): {ipv4_address}")
                LOG.info(f"Your IP address is (REQUEST): {requests.get('https://api.ipify.org').text}")
            except:
                raise

        def unset(*args):
            if len(args) > 0 and args[0] == "help":
                return ['''Unset proxy server''', ["N/A"]]
            try:
                socket.socket = ORIGIN_SOCKET
            except:
                raise

        def test(*args):
            if len(args) > 0 and args[0] == "help":
                return ['''Test proxy connection''', ["N/A"]]
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("ifconfig.me", 80))
                s.sendall(b"GET / HTTP/1.1\r\nHost: ifconfig.me\r\nConnection: close\r\n\r\n")
                response = s.recv(4096).decode()
                s.close()

                ipv4_address = response.split("\r\n\r\n")[1].strip()
                LOG.info(f"Your IP address is (SOCKET): {ipv4_address}")
                LOG.info(f"Your IP address is (REQUEST): {requests.get('https://api.ipify.org').text}")
            except:
                raise
            
    class var:
        def set(*args):
            if len(args) > 0 and args[0] == "help":
                return ['''Set local variable''', ["KEY", "VALUE"]]
            try:
                target = str(args[0])
                value = str(args[1])
                if target in settings:
                    old = settings[target]
                    settings[target] = value
                    LOG.info(f"[+] Variable successfully changed: {old} --> {value}")
                elif not target in settings:
                    LOG.info(f"[-] Variable change failed: variable not exists")
                else:
                    LOG.info(f"[-] Variable change failed: Unknown")
            except:
                raise
        def print(*args):
            if len(args) > 0 and args[0] == "help":
                return ['''print local variable.\nType 'all' to see all local variables''', ["KEY"]]
            try:
                target = str(args[0])
                if target in settings:
                    LOG.info(f"{target}{' ' * (32 - len(str(target)))}: {settings[target]}")
                elif target == "all":
                    for key in settings:
                        LOG.info(f"{key}{' ' * (32 - len(str(key)))}: {settings[key]}")
                elif not target in settings:
                    LOG.info(f"[-] Variable print failed: variable not exists")
                else:
                    LOG.info(f"[-] Variable print failed: Unknown")
            except:
                raise
        def reset(*args):
            if len(args) > 0 and args[0] == "help":
                return ['''Reset local variables''', ["N/A"]]
            Setting()

class Handler:
    def __init__(self, command):
        self.COMMAND = str(command)
        self.ObjectSplit = "."
        self.ArgumentsSplit = " "
        self.arguments = []
        self.object = Shell
    def execute(self):
        Type = self.COMMAND.split(self.ObjectSplit)[0]
        Func = self.COMMAND.split(self.ObjectSplit)[1].split(self.ArgumentsSplit)[0]
        arguments = self.COMMAND.split(self.ArgumentsSplit)[1:]
        getattr(getattr(self.object, Type), Func)(*arguments)

if __name__ == "__main__":
    Setting()
    if "-c" in sys.argv:
        LOGGER.setLevel(logging.INFO)
        command = " ".join(sys.argv).split("-c")[1][1:]
        obj = Handler(command=command)
        obj.execute()
        sys.exit(0)
    LOGGER.setLevel(logging.DEBUG)
    while True:
        try:
            command = str(input(f"Katana {Local_Version} > "))
            if command == "clear" or command == "cls": os.system("cls" if os.name == "nt" else "clear")
            elif command == "exit": break
            elif command == "": continue
            elif command == "help":
                for Type in Shell.__dict__:
                    if not Type.startswith("__"):
                        LOG.info(f"[{Type}]")
                        commands = getattr(Shell, Type).__dict__
                        for func in commands:
                            if not func.startswith("__"):
                                help_object = getattr(getattr(Shell, Type), func)('help')
                                helptext = help_object[0]
                                help_args = help_object[1]

                                help_command = f"{f'{Type}.{func}':<30}"
                                if "\n" in helptext:
                                    helptext += ''.rjust(60-len(helptext.split("\n")[-1]), " ")
                                    helptext = str(helptext).replace("\n", f"\n{' ' * 30}")
                                else:
                                    helptext = f"{helptext:<60}"
                                LOG.info(f"{help_command}{helptext}{' '.join(help_args)}")
                        LOG.info("")
            else:
                obj = Handler(command=command)
                obj.execute()
                LOG.info("")
        except:
            LOG.info(f"{traceback.format_exc()}")