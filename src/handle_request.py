import uuid
import json
import time
import requests
from config import ENABLE_DEBUG_NOFORWARD
from helpers.uwsgi_headers_parser import parse_uwsgi_request_headers
from redis_cluster import RedisCluster
from redis_cluster.functions import deregister_domain_hit, register_domain_hit





def raiserr(http_status, message, start_response):
    """ Initialize UWSGI error response to be returned at the entry handler"""
    start_response(str(http_status), [('Content-Type', 'application/json')])
    ex_js = {
        "error": message
    }
    
    return [json.dumps(ex_js).encode('utf-8')]

def response(http_status, data: any, start_response):
    """ Initialize UWSGI response to be returned at the entry handler"""
    start_response(str(http_status), [('Content-Type', 'application/json')])

    if isinstance(data,dict):
        return [json.dumps(data).encode('utf-8')]
    elif isinstance(data,str):
        return [data.encode('utf-8')]
    elif isinstance(data,int):
        return [str(data).encode('utf-8')]
    else:
        # Unsupported data type
        return [b"{}"]




def handle_proxy_request(env,start_response):
    """ Proxifies the request """

    request_headers = parse_uwsgi_request_headers(env)

    # Parse the target domain subject to rate limiting
    target_domain = request_headers['x-crawler-thread-domain']

    if not target_domain :
        return raiserr('400 Bad Request', "Must pass 'HTTP_X_CRAWLER_THREAD_DOMAIN'", start_response)
        
    

    # Register hit count
    hit_registered_successfully = register_domain_hit(target_domain)

    if not hit_registered_successfully:
        return raiserr('429 Rate Limited', "Rate was limited for domain %s " % (target_domain), start_response)

    try:
        if not ENABLE_DEBUG_NOFORWARD:
            endpoint_response = forward_request(env,request_headers)
            return response(endpoint_response.status_code, endpoint_response.text,start_response)
        else:
            time.sleep(3)
            return response(200, '{}',start_response)
    except Exception as ex:
        return raiserr(500,str(ex),start_response)
    finally:
        deregister_domain_hit(target_domain)
        

def forward_request(env, headers) -> requests.Response:
    """ Forward the request received in the proxy environment and return the response"""

    request_method =  str(env.get('REQUEST_METHOD', 'get')).lower() # Default to get
    
    callable_target = getattr(requests,request_method)

    return callable_target(url=env['REQUEST_URI'], headers=headers)
