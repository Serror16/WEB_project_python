from functools import wraps
from flask import request, jsonify
from marshmallow import Schema, ValidationError
from typing import Type


def validate_request(schema_class: Type[Schema]):
    """
    Декоратор для валидации входящих JSON запросов
    
    Использование:
    @validate_request(TaxReportRequest)
    def create_report(data):

        ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            json_data = request.get_json(silent=True)
            
            if not json_data:
                return jsonify({
                    "error_code": "INVALID_JSON",
                    "message": "Тело запроса должно быть валидным JSON",
                    "details": {}
                }), 400
            
            schema = schema_class()
            try:
                validated_data = schema.load(json_data)
            except ValidationError as err:
                return jsonify({
                    "error_code": "VALIDATION_ERROR",
                    "message": "Ошибка валидации данных",
                    "details": err.messages
                }), 422
            
            return f(validated_data, *args, **kwargs)
        
        return decorated
    
    return decorator


def validate_query_params(schema_class: Type[Schema]):
    """
    Декоратор для валидации query параметров
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            query_data = request.args.to_dict()
            
            schema = schema_class()
            try:
                validated_data = schema.load(query_data)
            except ValidationError as err:
                return jsonify({
                    "error_code": "VALIDATION_ERROR",
                    "message": "Ошибка валидации параметров",
                    "details": err.messages
                }), 422
            
            kwargs['query_params'] = validated_data
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator