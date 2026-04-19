import requests

from flask import Blueprint, jsonify, current_app, request
from reliabackend.auth import get_current_user

labsland_ai_blueprint = Blueprint('labsland_ai', __name__)
LABSLAND_AI_TIMEOUT_SECONDS = 15

@labsland_ai_blueprint.before_request
def before_request():
    current_user = get_current_user()
    if current_user['anonymous']:
        return _corsify_actual_response(jsonify(success=False, redirect_to=current_app.config['REDIRECT_URL'], user_id=None, session_id=None, locale=None))

    if not current_user['active'] or current_user['time_left'] <= 0:
        return _corsify_actual_response(jsonify(success=False, redirect_to=current_user['redirect_to'], user_id=None, session_id=None, locale=None))

@labsland_ai_blueprint.route('/conversations/<conversation_id>', methods=['POST'])
def conversations(conversation_id: str):
    current_user = get_current_user()

    request_data = request.get_json(force=True, silent=True)
    if not isinstance(request_data, dict):
        return jsonify(success=False, message='A JSON body is required'), 400

    message = request_data.get('message')
    if not message:
        return jsonify(success=False, message='Message is required'), 400

    # This is the raw, client-side context.
    context = request_data.get('context')
    if context is None:
        return jsonify(success=False, message="No context field provided"), 400
    if not isinstance(context, (dict, str)):
        return jsonify(success=False, message="Context must be a dictionary or str"), 400
    if isinstance(context, str):
        context = {"context": context}

    request_conversations = current_user.get('conversations') or {}
    anonymized_reservation_id = request_conversations.get("anonymizedReservationId")
    agent = request_conversations.get("agent")
    session_id = current_user['session_id']

    try:
        response = requests.post(
            f"https://api.labsland.com/ai/conversations/external-labs/{conversation_id}",
            json={
                'sessionId': session_id,
                'conversationId': conversation_id,
                'message': message,
                'context': context,
                'agent': agent,
                'anonymizedReservationId': anonymized_reservation_id
            },
            timeout=LABSLAND_AI_TIMEOUT_SECONDS
        )
    except requests.RequestException:
        current_app.logger.exception("Error calling LabsLand AI Assistant")
        return jsonify({
            'success': False,
            'message': "Unable to reach the LabsLand AI Assistant right now."
        }), 502

    response_json = _safe_response_json(response)

    if not response.ok:
        message = _extract_error_message(response_json, response)
        current_app.logger.warning(
            "LabsLand AI Assistant rejected the request",
            extra={
                'conversation_id': conversation_id,
                'upstream_status': response.status_code,
                'upstream_message': message,
            }
        )
        return jsonify({
            'success': False,
            'message': message,
            'upstreamStatus': response.status_code,
        }), response.status_code

    if not isinstance(response_json, dict):
        current_app.logger.error("LabsLand AI Assistant returned an invalid success payload")
        return jsonify({
            'success': False,
            'message': "LabsLand AI Assistant returned an invalid response."
        }), 502

    return jsonify({
        'success': response_json.get('success'),
        'messageId': response_json.get('messageId'),
        'messageUrl': response_json.get('messageUrl')
    })


def _safe_response_json(response):
    try:
        return response.json()
    except ValueError:
        return None


def _extract_error_message(response_json, response):
    if isinstance(response_json, dict):
        message = response_json.get('message')
        if message:
            return message

    response_text = (response.text or '').strip()
    if response_text:
        return response_text

    return f"LabsLand AI Assistant request failed with status {response.status_code}."


def _corsify_actual_response(response):
    response.headers['Access-Control-Allow-Origin'] = '*';
    response.headers['Access-Control-Allow-Credentials'] = 'true';
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, GET, POST';
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, If-Modified-Since, X-File-Name, Cache-Control';
    return response
