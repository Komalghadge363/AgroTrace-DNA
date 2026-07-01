from flask import jsonify

class APIError(Exception):
    """Custom API Exception"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = self.status_code
        return rv

def register_error_handlers(app):
    """Register error handlers for the Flask app"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'message': 'Bad request', 'status': 400}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'message': 'Unauthorized', 'status': 401}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'message': 'Forbidden', 'status': 403}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Resource not found', 'status': 404}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        response = {
            'message': 'Method not allowed',
            'status': 405
        }
        if getattr(error, 'valid_methods', None):
            response['allowed_methods'] = [
                method for method in error.valid_methods
                if method not in {'HEAD', 'OPTIONS'}
            ]
        return jsonify(response), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'message': 'Internal server error', 'status': 500}), 500
