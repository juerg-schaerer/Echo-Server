from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime
from functools import wraps
from apispec import APISpec
from typing import Optional, Dict, Any

# Initialize API Spec
spec = APISpec(
    title="Echo Server API",
    version="1.0.0",
    openapi_version="3.0.0",
    info=dict(description="A simple echo server that returns headers and request data"),
)

def endpoint(path: str, methods: list, summary: str, response_schema: Dict[str, Any]):
    """Decorator to register endpoints and their OpenAPI specifications"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        
        # Register the path in OpenAPI spec
        for method in methods:
            spec.path(
                path=path,
                operations={
                    method.lower(): {
                        'summary': summary,
                        'responses': {
                            '200': {
                                'description': 'Successful response',
                                'content': {
                                    'application/json': {
                                        'schema': response_schema
                                    }
                                }
                            },
                            '400': {
                                'description': 'Bad Request',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'properties': {
                                                'error': {'type': 'string'},
                                                'detail': {'type': 'string'}
                                            }
                                        }
                                    }
                                }
                            },
                            '415': {
                                'description': 'Unsupported Media Type',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'properties': {
                                                'error': {'type': 'string'},
                                                'supported_types': {
                                                    'type': 'array',
                                                    'items': {'type': 'string'}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            )
        return wrapper
    return decorator

class EchoHandler(BaseHTTPRequestHandler):
    def send_error_response(self, status_code: int, error_message: dict):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(error_message, indent=2).encode('utf-8'))

    @endpoint(
        path='/header',
        methods=['GET', 'POST', 'PUT', 'DELETE'],
        summary='Get request headers',
        response_schema={
            'type': 'object',
            'properties': {
                'timestamp': {'type': 'string'},
                'request': {
                    'type': 'object',
                    'properties': {
                        'method': {'type': 'string'},
                        'headers': {'type': 'object'},
                        'client_address': {'type': 'string'},
                        'client_port': {'type': 'integer'}
                    }
                }
            }
        }
    )
    def handle_headers(self):
        return {
            'timestamp': datetime.now().isoformat(),
            'request': {
                'method': self.command,
                'headers': dict(self.headers),
                'client_address': self.client_address[0],
                'client_port': self.client_address[1]
            }
        }

    @endpoint(
        path='/all',
        methods=['GET', 'POST', 'PUT', 'DELETE'],
        summary='Get all request data',
        response_schema={
            'type': 'object',
            'properties': {
                'timestamp': {'type': 'string'},
                'request': {
                    'type': 'object',
                    'properties': {
                        'method': {'type': 'string'},
                        'path': {'type': 'string'},
                        'protocol_version': {'type': 'string'},
                        'headers': {'type': 'object'},
                        'content_length': {'type': 'integer'},
                        'body': {'type': 'string'},
                        'client_address': {'type': 'string'},
                        'client_port': {'type': 'integer'}
                    }
                }
            }
        }
    )
    def handle_all(self, body):
        return {
            'timestamp': datetime.now().isoformat(),
            'request': {
                'method': self.command,
                'path': self.path,
                'protocol_version': self.protocol_version,
                'headers': dict(self.headers),
                'content_length': len(body),
                'body': body.decode('utf-8') if body else None,
                'client_address': self.client_address[0],
                'client_port': self.client_address[1]
            }
        }

    def _handle_request(self):
        try:
            # Check content type for POST/PUT requests
            if self.command in ['POST', 'PUT']:
                content_type = self.headers.get('Content-Type', '')
                if content_type and 'application/json' not in content_type.lower():
                    self.send_error_response(415, {
                        'error': 'Unsupported Media Type',
                        'supported_types': ['application/json']
                    })
                    return

            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''

            # Validate JSON body for POST/PUT requests
            if self.command in ['POST', 'PUT'] and content_length > 0:
                try:
                    json.loads(body)
                except json.JSONDecodeError:
                    self.send_error_response(400, {
                        'error': 'Bad Request',
                        'detail': 'Invalid JSON payload'
                    })
                    return

            if self.path == '/openapi':
                response = spec.to_dict()
            elif self.path == '/header':
                response = self.handle_headers()
            elif self.path == '/all':
                response = self.handle_all(body)
            else:
                self.send_error_response(404, {
                    'error': 'Not Found',
                    'available_endpoints': ['/header', '/all', '/openapi']
                })
                return

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))

            # Print debug info
            print(f"\n{'='*50}")
            print(f"Received {self.command} request at {datetime.now().isoformat()}")
            print(f"Path: {self.path}")
            print(f"Headers size: {len(self.headers)} items")
            print(f"Payload size: {len(body)} bytes")
            print(f"Client: {self.client_address[0]}:{self.client_address[1]}")
            print(f"{'='*50}\n")

        except Exception as e:
            self.send_error_response(500, {
                'error': 'Internal Server Error',
                'detail': str(e)
            })

    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def do_PUT(self):
        self._handle_request()

    def do_DELETE(self):
        self._handle_request()

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, EchoHandler)
    print(f"Echo Server running on http://localhost:{port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()