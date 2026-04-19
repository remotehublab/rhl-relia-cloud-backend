import unittest
from unittest.mock import Mock, patch

import requests

from reliabackend import create_app


class LabsLandAiViewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('development')
        cls.client = cls.app.test_client()

    def active_user(self):
        return {
            'username_unique': 'user-1',
            'session_id': 'session-1',
            'anonymous': False,
            'active': True,
            'time_left': 600,
            'locale': 'en',
            'redirect_to': 'https://example.com',
            'conversations': {
                'anonymizedReservationId': 'reservation-1',
                'agent': 'assistant-1',
            },
        }

    def mock_response(self, status_code, payload=None, text=None):
        response = Mock()
        response.status_code = status_code
        response.ok = 200 <= status_code < 300
        response.text = text if text is not None else ''
        if payload is None:
            response.json.side_effect = ValueError('no json')
        else:
            response.json.return_value = payload
        return response

    @patch('reliabackend.views.labsland_ai.requests.post')
    @patch('reliabackend.views.labsland_ai.get_current_user')
    def test_conversation_success_returns_message_identifiers(self, mock_get_current_user, mock_post):
        mock_get_current_user.return_value = self.active_user()
        mock_post.return_value = self.mock_response(200, {
            'success': True,
            'messageId': 'message-1',
            'messageUrl': 'https://api.labsland.com/messages/1',
        })

        response = self.client.post('/api/ai/conversations/conversation-1', json={
            'message': 'hello',
            'context': {}
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            'success': True,
            'messageId': 'message-1',
            'messageUrl': 'https://api.labsland.com/messages/1',
        })
        mock_post.assert_called_once()
        self.assertEqual(mock_post.call_args.kwargs['timeout'], 15)

    @patch('reliabackend.views.labsland_ai.requests.post')
    @patch('reliabackend.views.labsland_ai.get_current_user')
    def test_upstream_http_error_preserves_status_and_message(self, mock_get_current_user, mock_post):
        mock_get_current_user.return_value = self.active_user()
        upstream_message = 'The laboratory session was not made from an institution (uw) supporting AI'
        mock_post.return_value = self.mock_response(400, {
            'success': False,
            'message': upstream_message,
        }, text='{"success": false}')

        response = self.client.post('/api/ai/conversations/conversation-1', json={
            'message': 'hello',
            'context': {}
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
            'success': False,
            'message': upstream_message,
            'upstreamStatus': 400,
        })

    @patch('reliabackend.views.labsland_ai.requests.post')
    @patch('reliabackend.views.labsland_ai.get_current_user')
    def test_network_failure_returns_gateway_error(self, mock_get_current_user, mock_post):
        mock_get_current_user.return_value = self.active_user()
        mock_post.side_effect = requests.RequestException('boom')

        response = self.client.post('/api/ai/conversations/conversation-1', json={
            'message': 'hello',
            'context': {}
        })

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.get_json(), {
            'success': False,
            'message': 'Unable to reach the LabsLand AI Assistant right now.'
        })

    @patch('reliabackend.views.labsland_ai.get_current_user')
    def test_missing_json_body_is_rejected(self, mock_get_current_user):
        mock_get_current_user.return_value = self.active_user()

        response = self.client.post(
            '/api/ai/conversations/conversation-1',
            data='not-json',
            content_type='text/plain'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {
            'success': False,
            'message': 'A JSON body is required'
        })


if __name__ == '__main__':
    unittest.main()
