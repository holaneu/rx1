def fetch_api():
    """ Dummy stand-in for a real HTTP/API call"""
    import time
    time.sleep(1)
    return list(range(5))