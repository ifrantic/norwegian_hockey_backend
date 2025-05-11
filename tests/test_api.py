import unittest
from src.api.routes import app

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_endpoint(self):
        response = self.app.get('/api/some_endpoint')
        self.assertEqual(response.status_code, 200)
        self.assertIn('expected_key', response.json)

    def test_post_endpoint(self):
        response = self.app.post('/api/some_endpoint', json={'key': 'value'})
        self.assertEqual(response.status_code, 201)
        self.assertIn('expected_key', response.json)

if __name__ == '__main__':
    unittest.main()