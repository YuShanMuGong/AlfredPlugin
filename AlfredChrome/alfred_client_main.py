# coding=utf-8
import json
import sys
import time
import urllib2
import config

if __name__ == "__main__":
    start_time = time.time() * 1000
    keyword = sys.argv[1]
    url = "http://localhost:8080/do_search"
    form = {"keyword": keyword, "keyword1": keyword}
    req = urllib2.Request(url,
                          data=json.dumps(form),
                          headers={'Content-Type': 'application/json'})
    response = urllib2.urlopen(req)
    result = response.read()
    end_time = time.time() * 1000
    if config.IS_DEBUG_MODE:
        sys.stdout.write(result.decode("unicode_escape").encode("utf-8"))
        print "\nrt = {}".format(end_time - start_time)
    else:
        sys.stdout.write(result)
    sys.stdout.flush()
    exit(0)
