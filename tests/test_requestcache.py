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

import mock
import unittest

from swift.common.swob import Request

from requestcache import middleware


class FakeApp(object):
    def __call__(self, env, start_response):
        start_response('200 OK', [], "")
        return []


def start_response(*args):
    pass


class TestRequestCache(unittest.TestCase):
    def setUp(self):
        self.objname = '/v1/AUTH_test/container/obj'
        self.app = middleware.RequestCache(FakeApp(), {})
        self.memcache_key = 'RequestCache/AUTH_test/container/obj'
        self.app.memcache.delete(self.memcache_key)

    def tearDown(self):
        self.app.memcache.delete(self.memcache_key)

    @mock.patch('swift.common.wsgi.make_subrequest')
    def test_get(self, mock_subrequest):
        mock_subrequest.return_value.get_response.return_value.body = "data"

        # First Request is not cached
        req = Request.blank(self.objname)
        res = req.get_response(self.app)
        self.assertEqual(res.status_int, 200)
        self.assertFalse('X-Requestcache' in res.headers)

        # Second request is cached
        req = Request.blank(self.objname)
        res = req.get_response(self.app)
        self.assertEqual(res.status_int, 200)
        self.assertTrue('X-Requestcache' in res.headers)


if __name__ == '__main__':
    unittest.main()
