import os
import requests
from time import sleep
from configparser import ConfigParser
from os import system, name
from threading import Thread, active_count
from re import search, compile
from IPython.display import clear_output
import csv
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
 
software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value, SoftwareName.EDGE.value, SoftwareName.OPERA.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MAC.value]

user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=1200)

THREADS = 600
PROXIES_TYPES = ('http', 'socks4', 'socks5')
USER_AGENTT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
REGEX = compile(r"(?:^|\D)?(("+ r"(?:[1-9]|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
                + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
                + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
                + r"\." + r"(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"
                + r"):" + (r"(?:\d|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{3}"
                + r"|65[0-4]\d{2}|655[0-2]\d|6553[0-5])")
                + r")(?:\D|$)")

errors = open('errors.txt', 'a+')
cfg = ConfigParser(interpolation=None)
cfg.read("config.ini", encoding="utf-8")

http, socks4, socks5 = '', '', ''
try: http, socks4, socks5 = cfg["HTTP"], cfg["SOCKS4"], cfg["SOCKS5"]
except KeyError: print(' [ OUTPUT ] Error | config.ini not found!');sleep(3);exit()

proxy_errors, token_errors = 0, 0
channel, post, time_out, real_views = '', 0, 15, 0
    
def save_waste_proxies(proxies):
    with open('waste_proxy.txt', 'a') as file:
        for proxy in proxies:
            file.write(proxy + '\n')
            
            
def control(proxy, proxy_type):
    global proxy_errors, token_errors
    with open('url.csv', 'r') as csvfile:
       reader = csv.reader(csvfile)
       urls = [row for row in reader]
    for url in urls:
        USER_AGENT = user_agent_rotator.get_random_user_agent()
        channel, post = url[0].split('/')[-2], url[0].split('/')[-1]
        try:
            session = requests.session()
            response = session.get(f'https://t.me/{channel}/{post}', params={'embed': '1', 'mode': 'tme'},
                                   headers={'referer': f'https://t.me/{channel}/{post}', 'user-agent': USER_AGENT},
                                   proxies={'http': f'{proxy_type}://{proxy}', 'https': f'{proxy_type}://{proxy}'},
                                   timeout=time_out)
            token = search('data-view="([^"]+)', response.text).group(1)
            cookies_dict = session.cookies.get_dict()
            response = session.get('https://t.me/v/', params={'views': str(token)}, cookies={
                'stel_dt': '-240', 'stel_web_auth': 'https%3A%2F%2Fweb.telegram.org%2Fz%2F',
                'stel_ssid': cookies_dict.get('stel_ssid', None), 'stel_on': cookies_dict.get('stel_on', None)},
                                headers={'referer': f'https://t.me/{channel}/{post}?embed=1&mode=tme',
                                    'user-agent': USER_AGENT, 'x-requested-with': 'XMLHttpRequest'},
                                proxies={'http': f'{proxy_type}://{proxy}', 'https': f'{proxy_type}://{proxy}'},
                                timeout=time_out)
                            
            if response.status_code == 200 and response.text == 'true':
                return True
            else:
                return False
        except AttributeError:
            token_errors += 1
            save_waste_proxies([proxy])
        except requests.exceptions.RequestException:
            proxy_errors += 1
            save_waste_proxies([proxy])
        except Exception as e: return errors.write(f'{e}\n')
        
        

def get_views_from_saved_proxies(proxy_type, proxies):
    for proxy in proxies:
        control(proxy.strip(), proxy_type)

def start_view():
    while True:
            threads = []
            for proxy_type in PROXIES_TYPES:
                with open(f"{proxy_type}_proxies.txt", 'r') as file:
                    proxies = file.readlines()
                chunked_proxies = [proxies[i:i + 70] for i in range(0, len(proxies), 70)]
                for chunk in chunked_proxies:
                    thread = Thread(target=get_views_from_saved_proxies, args=(proxy_type, chunk))
                    threads.append(thread)
                    thread.start()
            for t in threads:
                t.join()

        
E = '\033[1;31m'
B = '\033[2;36m'
G = '\033[1;32m'
S = '\033[1;33m'

def check_views():
    global real_views
    while True:
        with open('url.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            urls = [row for row in reader]
        print(urls)
        for url in urls:
            channel, post = url[0].split('/')[-2], url[0].split('/')[-1]
            telegram_request = requests.get(f'https://t.me/{channel}/{post}', params={'embed': '1', 'mode': 'tme'},
                                            headers={'referer': f'https://t.me/{channel}/{post}', 'user-agent': USER_AGENTT})
            real_views = search('<span class="tgme_widget_message_views">([^<]+)', telegram_request.text).group(1)
            print(f'{B}[ LIVE VIEWS ]: {G}{real_views} ✅ {B}for {url[0]}')
            print(f'{S}[ CONNECTION ERRORS ]: {E}{proxy_errors} 🚫')
            print(f'{S}[ TOKEN ERRORS ]: {E}{token_errors} ❌')
            print(f'{G}[ THREADS ]: {B}{active_count()} ⇝⇝⇝⇝ ')

        sleep(300)

Thread(target=start_view).start()
Thread(target=check_views).start()