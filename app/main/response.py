from flask import jsonify

class HTTPRequestException(Exception):
    def __init__(self, message, status_code=None, payload=None):
        super().__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        else:
            self.status_code = 400
        self.payload = payload

    def __str__(self):
        return f"HTTPRequestException: {self.message} (Status: {self.status_code})"

    def to_dict(self):
        error_dict = dict()

        if self.payload:
            error_dict['payload'] = self.payload

        error_dict['message'] = self.message
        return error_dict

    def to_response(self):
        response = jsonify(self.to_dict())
        response.status_code = self.status_code
        return response
    

class HTTPRequestSuccess:
    def __init__(self, message, status_code=None, payload=None):
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        else:
            self.status_code = 200
        self.payload = payload

    def to_dict(self):
        success_dict = dict()

        if self.payload:
            success_dict['payload'] = self.payload

        success_dict['message'] = self.message
        return success_dict

    def to_response(self):
        response = jsonify(self.to_dict())
        response.status_code = self.status_code
        return response
