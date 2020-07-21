import unittest
from flask import json

from household_api import app


class BasicTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tester = app.test_client()
        json_text = '''
        {"income":50000,"members":[{"age":45,"gender":"female"},\
            {"age":40,"gender":"male"}]}
        '''
        response = cls.tester.post('/household/',
                                    data=json.dumps(json.loads(json_text)),
                                    content_type='application/json',
                                    follow_redirects=True).get_data()
        cls.test_id = response.replace('"', '').rstrip()

        large_json_text = '''
        {"income":50000,"members":[{"age":45,"gender":"female"},\
            {"age":40,"gender":"male"},{"age":45,"gender":"female"},\
            {"age":45,"gender":"female"},{"age":45,"gender":"female"},\
            {"age":45,"gender":"female"},{"age":45,"gender":"female"},\
            {"age":45,"gender":"female"},{"age":45,"gender":"female"},\
            {"age":45,"gender":"female"}]}
        '''
        response = cls.tester.post('/household/',
                                    data=json.dumps(json.loads(large_json_text)),
                                    content_type='application/json',
                                    follow_redirects=True).get_data()
        cls.large_test_id = response.replace('"', '').rstrip()

    def test_household_create(self):
        """Ensure that user can create households """
        json_text = '''
        {"income":50000,"members":[{"age":45,"gender":"female"},\
            {"age":40,"gender":"male"}]}
        '''
        response = self.tester.post('/household/',
                                    data=json.dumps(json.loads(json_text)),
                                    content_type='application/json',
                                    follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # json_response = response.get_data(as_text=True)
        # print json_response

    def test_household_bad_create(self):
        """Ensure that user will get a 400 response on an invalid post  """
        tester = app.test_client(self)
        response = tester.post('/household/', data = {}, follow_redirects=True)
        self.assertEqual(response.status_code, 400)

    def test_sample(self):
        """Ensure that user can get sample households """
        response = self.tester.get('/sample-household/',
                                   content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_household_get(self):
        """Ensure that user can get households by id"""
        url = '/household/'+ self.test_id + '/'
        response = self.tester.get(url,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_household_get_fpl(self):
        """Ensure that user can get households fpl"""
        url = '/household/'+ self.test_id + '/fpl-percent/'
        response = self.tester.get(url,
                              content_type='application/json')
        num = float(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(num, 3.0376670716889427)

    def test_household_get_fpl_large(self):
        """Ensure that user can get larger than 8 members households fpl"""
        url = '/household/'+ self.large_test_id + '/fpl-percent/'
        response = self.tester.get(url,
                              content_type='application/json')
        num = float(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(num, 0.9800078400627205)



if __name__ == '__main__':
    unittest.main()
