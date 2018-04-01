from __future__ import unicode_literals
#coding=utf-8

import requests
import unittest
# Create your tests here.

class GetEventlisttest(unittest.TestCase):
    def setUp(self):
        self.url = "http://127.0.0.1:8000/get_event_list/"
    def test_get_event_list_null(self):
        r = requests.get(self.url,params={'eid':''})
        result = r.json()
        print result
        self.assertEqual(result['status'],10021)
        self.assertEqual(result['message'],"parameter error")
    def test_get_event_list_success(self):
        r = requests.get(self.url,params={'eid':'2'})
        result = r.json()
        print result
        self.assertEqual(result['status'],200)
        self.assertEqual(result['message'],'success')

if __name__ == '__main__':
        unittest.main()

