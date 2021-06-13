from mmap import MAP_EXECUTABLE
from config import DOMAIN_RATE_LIMIT, ENABLE_DEBUG_OUTPUT
import time
from redis_cluster import RedisCluster
from redis_cluster.keys import CRAWLER_STREAM_DOMAINS_IN_PROCESS_COUNTER


def register_domain_hit(domain: str) -> bool: 
        """ 
            Will attempt to occupy a domain slot.
            Returns True on whether the domain was occupied, or False if no slots available
        """


        
        conn = RedisCluster.get_connection()
    
        """ Start a transactional check-and-set """
        #conn.watch('CRAWLER_STREAM_DOMAINS_IN_PROCESS_COUNTER')
        
        increment_or_fail_callable = conn.register_script("""
            local counter = redis.call("hget",ARGV[1], ARGV[2]) or 0
            if tonumber(counter) >= tonumber(ARGV[3]) then
                return false
            else
                return redis.call('hincrby',ARGV[1],ARGV[2],1)
            end
        """)


        with conn.pipeline() as pipe:

            increment_or_fail_callable(args=[CRAWLER_STREAM_DOMAINS_IN_PROCESS_COUNTER,domain, DOMAIN_RATE_LIMIT],client=pipe)
            execution_result = pipe.execute()[0]
            if not execution_result:
                print(f'[{domain}] Rate limiter triggered')

            elif ENABLE_DEBUG_OUTPUT:
                print(f'[{domain}] = {execution_result} (+1)')
            
            return execution_result
            
        #print(conn.hgetall(CRAWLER_STREAM_DOMAINS_IN_PROCESS_COUNTER))
#        current_rate = int(conn.get('CRAWLER_STREAM_DOMAINS_IN_PROCESS_COUNTER'))

        # conn.hincrby('CRAWLER_STREAM_DOMAINS_IN_PROCESS_COUNTER',domain,1)
        

        # if current_rate >= DOMAIN_RATE_LIMIT :
        #         if ENABLE_DEBUG_OUTPUT:
        #             print(f'[RateLimiter] Hit for {domain}')
        #         return False

        # conn.hincrby('CRAWLER_STREAM_DOMAINS_IN_PROCESS_COUNTER',domain,1)

        return True



def reset_domain_hits(domain: str = None) -> bool: 
        """ 
            Will clear hit counter for domain, if passed.
            If <domain> is None, will reset all counters
        """


        
        conn = RedisCluster.get_connection()
    
        if domain is None:
            conn.delete(CRAWLER_STREAM_DOMAINS_IN_PROCESS_COUNTER)
        else:
            conn.hset(CRAWLER_STREAM_DOMAINS_IN_PROCESS_COUNTER,domain,0)

        return True
                
    
def deregister_domain_hit(domain):
    """
        Decrease domain counter hits by 1
    """


    conn = RedisCluster.get_connection()

    if domain is None:
        raise "Must provide domain"

    new_value = conn.hincrby(CRAWLER_STREAM_DOMAINS_IN_PROCESS_COUNTER,domain,-1)   

    if ENABLE_DEBUG_OUTPUT:
        print(f'[{domain}] = {new_value} (-1)')

    return True
        
