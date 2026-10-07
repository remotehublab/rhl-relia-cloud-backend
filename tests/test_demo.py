import unittest
from unittest.mock import Mock, patch
from flask import Flask
from reliabackend.demo import demo_for_server_data, flowgraphs
from reliabackend.views.user import user_blueprint
from reliabackend.views.files import files_blueprint
from reliabackend.views.data import data_blueprint

class DemoTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(SCHEDULER_BASE_URL='https://example.com', SCHEDULER_TOKEN='test', UPLOAD_FOLDER='/unused')
        self.app.register_blueprint(user_blueprint, url_prefix='/api/user')
        self.app.register_blueprint(files_blueprint, url_prefix='/api/user/files')
        self.app.register_blueprint(data_blueprint, url_prefix='/api/data')
        self.client = self.app.test_client()
        self.user = {'anonymous':False,'active':True,'time_left':60,'username_unique':'demo','session_id':'test-session','demo':{'variant':'pluto-tone-spectrum'}}

    def test_only_trusted_server_demo_variant_enables_demo(self):
        self.assertIsNone(demo_for_server_data({}))
        self.assertIsNone(demo_for_server_data({'labsland_demo':{'enabled':True,'relia_variant':'unknown'}}))
        self.assertIsNotNone(demo_for_server_data({'labsland_demo':{'enabled':True,'relia_variant':'pluto-tone-spectrum'}}))

    def test_fixed_graphs_reject_arbitrary_tones_and_code(self):
        for value in ('evil', '<script>', 2450000000):
            with self.assertRaises(ValueError):flowgraphs(value)
        graphs=flowgraphs('high')
        self.assertIn("'125000'", graphs['transmitter']['content'])
        self.assertIn("attenuation1: '40'",graphs['transmitter']['content'])

    @patch('reliabackend.views.user.requests.post')
    @patch('reliabackend.views.user.delete_existing_session_data')
    @patch('reliabackend.views.user.get_current_user')
    def test_demo_schedules_fixed_pair_without_uploaded_files(self,user,delete,post):
        user.return_value=self.user;post.return_value=Mock(json=lambda:{'success':True,'taskIdentifier':'demo-task'})
        response=self.client.post('/api/user/tasks/',json={'tone':'low','grc_files':{'receiver':'untrusted'}})
        self.assertEqual(response.status_code,200)
        self.assertTrue(response.json['success'])
        payload=post.call_args.kwargs['json']
        self.assertEqual(set(payload['grc_files']),{'receiver','transmitter'})
        self.assertNotIn('untrusted',payload['grc_files']['receiver']['content'])
        self.assertEqual(payload['session_id'],'test-session')

    @patch('reliabackend.views.user.get_current_user')
    def test_demo_rejects_bad_json_shape_and_tone(self,user):
        user.return_value=self.user
        for value in ([],['low'],{'tone':[]},{'tone':'evil'}):
            self.assertEqual(self.client.post('/api/user/tasks/',json=value).status_code,400)

    @patch('reliabackend.views.user.requests.post')
    @patch('reliabackend.views.user.delete_existing_session_data')
    @patch('reliabackend.views.user.get_current_user')
    def test_scheduler_failure_has_recoverable_message(self,user,delete,post):
        import requests
        user.return_value=self.user;post.side_effect=requests.Timeout()
        response=self.client.post('/api/user/tasks/',json={'tone':'low'})
        self.assertEqual(response.status_code,503)
        self.assertIn('Please try again',response.json['message'])

    @patch('reliabackend.views.data.get_current_user')
    def test_expired_session_cannot_poll_runtime_data(self,user):
        user.return_value=dict(self.user,active=False,time_left=0)
        self.assertEqual(self.client.get('/api/data/tasks/task/devices').status_code,401)

    @patch('reliabackend.views.files.get_current_user')
    def test_demo_upload_and_metadata_changes_are_denied(self,user):
        user.return_value=self.user
        for endpoint in ('/api/user/files/','/api/user/files/metadata/test.grc'):
            self.assertEqual(self.client.post(endpoint,json={}).status_code,403)

    @patch('reliabackend.views.files.get_current_user')
    def test_expired_file_access_is_rejected_before_username_path(self,user):
        user.return_value=dict(self.user,active=False,time_left=0,username_unique=None)
        self.assertEqual(self.client.get('/api/user/files/').status_code,401)

    @patch('reliabackend.views.data.get_current_user')
    def test_demo_cannot_change_runtime_block(self,user):
        user.return_value=self.user
        self.assertEqual(self.client.post('/api/data/tasks/task/devices/r/blocks/variable',json={'value':1}).status_code,403)

if __name__=='__main__':unittest.main()
