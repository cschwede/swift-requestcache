# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from swift.common.memcached import MemcacheRing
from swift.common.swob import Request, Response
from swift.common.utils import register_swift_info
from swift.common import wsgi


class RequestCache(object):

    def __init__(self, app, conf, *args, **kwargs):
        self.app = app
        _servers = conf.get('memcache_servers', '127.0.0.1:11211')
        servers = [s.strip() for s in _servers.split(',') if s.strip()]
        self.memcache = MemcacheRing(servers)

    def __call__(self, env, start_response):

        request = Request(env.copy())
        if request.method != "GET":
            return self.app(env, start_response)

        (version, acc, con, obj) = request.split_path(1, 4, False)
        if not obj:
            return self.app(env, start_response)

        memcache_key = 'RequestCache/%s/%s/%s' % (acc, con, obj)

        cached_content = self.memcache.get(memcache_key)
        if cached_content:
            response = Response(request=request, body=cached_content)
            response.headers['X-RequestCache'] = 'True'
            return response(env, start_response)

        sub_req = wsgi.make_subrequest(env)
        sub_resp = sub_req.get_response(self.app)
        self.memcache.set(memcache_key, sub_resp.body, time=86400.0)

        return self.app(env, start_response)


def filter_factory(global_conf, **local_conf):
    """Returns a WSGI filter app for use with paste.deploy."""
    conf = global_conf.copy()
    conf.update(local_conf)
    register_swift_info('RequestCache')

    def auth_filter(app):
        return RequestCache(app, conf)
    return auth_filter
