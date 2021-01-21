Openstack Swift Request Cache Middleware
========================================

**This code is not maintained and has been archived. Use at your own risk.**

``requestcache`` is a middleware that caches GET requests.

Current status
--------------
Proof of concept. Don't use in production yet!

Quick Install
-------------

1) Install requestcache:

    git clone git://github.com/cschwede/swift-requestcache.git
    cd swift-requestcache
    sudo python setup.py install

2) Add a filter entry for requestcache to your proxy-server.conf:
  
    [filter:requestcache]
    use = egg:requestcache#requestcache
    memcache_servers = 127.0.0.1:11211

3) Alter your proxy-server.conf pipeline and add requestcache after your
authentication middleware:

    [pipeline:main]
    pipeline = catch_errors healthcheck cache tempauth requestcache proxy-server

4) Restart your proxy server: 

    swift-init proxy reload

Done!

You might want to tune your memcached settings, for example increase the maximum
object size or total memory.
