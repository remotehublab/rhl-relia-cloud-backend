from flask import Blueprint, jsonify, current_app, request
from reliabackend.auth import get_current_user

labsland_ai_blueprint = Blueprint('labsland_ai', __name__)

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
    message = request_data.get('message')
    if not message:
        return jsonify(success=False, message='Message is required'), 400

    # This is the raw, client-side context.
    context = request.json.get('context')
    if context is None:
        return jsonify(success=False, message="No context field provided"), 400
    if not isinstance(context, (dict, str)):
        return jsonify(success=False, message="Context must be a dictionary or str"), 400
    if isinstance(context, str):
        context = {"context": context}

    request_conversations = current_user.get('conversations') or {}
    anonymized_reservation_id = request_conversations.get("anonymizedReservationId")

    session_id = current_user['session_id']

    response = request.post("https://labs.labsland.com/ai/external-labs/conversations", json={
        'sessionId': session_id,
        'conversationId': conversation_id,
        'message': message,
        'context': context,
        'anonymizedReservationId': anonymized_reservation_id
    }).json()

    return jsonify({
        'success': response.get('success'),
        'messageId': response.get('messageId'),
        'messageUrl': response.get('messageUrl')
    })


def _corsify_actual_response(response):
    response.headers['Access-Control-Allow-Origin'] = '*';
    response.headers['Access-Control-Allow-Credentials'] = 'true';
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, GET, POST';
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, If-Modified-Since, X-File-Name, Cache-Control';
    return response
