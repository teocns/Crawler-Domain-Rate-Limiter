from random import shuffle
import requests
from threading import Thread
from helpers.names import get_nickname




proxy = {
    'http':'http://localhost:5070'
}
# Threaded function snippet
def threaded(fn):
    """ 
    To use as decorator to make a function call threaded.
    Needs import
    from threading import Thread"""
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper



domains = []
for i in range(99):
    domains.append(get_nickname())

domains = domains * 7
shuffle(domains)



cnt = 0

@threaded
def f(domain):
    response = requests.get('http://webhook.site',proxies=proxy, headers={'X_CRAWLER_THREAD_DOMAIN': domain})
    print(response.status_code)
    print(response.text)
    global cnt
    cnt += 1
    print(f'Total responses: {cnt}')


for domain in domains:
    f(domain)
