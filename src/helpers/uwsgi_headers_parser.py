def parse_uwsgi_request_headers(env):
    """ Parses all dict keys from <env> variable and returns a normalized dictionary of headers """ 

    headers_dict = {}
    for key in env:
        key = str(key)
        if key.startswith('HTTP_'):    
            normalized_key = key.replace('HTTP_','',1).replace('_','-').lower()
            headers_dict[normalized_key] = env[key]            
    return headers_dict


    
