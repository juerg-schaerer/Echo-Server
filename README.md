# Echo Server

A simple HTTP server that echoes back request information, perfect for testing and debugging API calls. It provides detailed information about incoming HTTP requests including headers, payload, and other request metadata. It has an endpoint to generate an Open API Specification wich you can use to generate an API in WSO2 Api Manager.

## Features

- Multiple endpoints for different testing purposes
- OpenAPI/Swagger specification included
- Detailed request information
- Support for GET, POST, PUT, DELETE methods
- Error handling with proper HTTP status codes
- JSON response formatting
- Console logging for debugging

## Installation

1. Clone the repository:
```bash
git clone https://github.com/juerg-schaerer/Echo-Server.git
cd Echo-Server
```

2. Install required dependencies:
```bash
pip install apispec
```

## Usage

1. Start the server:
```bash
python echo-server.py
```

The server will start on http://localhost:8000

2. Available endpoints:
- /header - Returns request headers information
- /all - Returns complete request information including body
- /openapi - Returns OpenAPI specification

3. Example requests:
```bash
# Get headers information
curl http://localhost:8000/header

# Send POST request with JSON data
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}' \
  http://localhost:8000/all

# Get OpenAPI specification
curl http://localhost:8000/openapi
```

## Error Handling
The server handles various error cases with appropriate HTTP status codes:

- 400 Bad Request - Invalid JSON payload
- 404 Not Found - Invalid endpoint
- 415 Unsupported Media Type - Wrong content type
- 500 Internal Server Error - Server-side errors

Example error request:
```bash
# Trigger 415 error with wrong content type
curl -X POST \
  -H "Content-Type: text/plain" \
  -d "invalid data" \
  http://localhost:8000/all
 ```
 ## Integration with WSO2 API Manager
The server provides an OpenAPI specification that can be directly imported into WSO2 API Manager:

1. Get the OpenAPI specification:
```bash
curl http://localhost:8000/openapi > echo-api.json
 ```

2. In WSO2 API Manager Publisher portal:
   - Create new API
   - Choose "Import OpenAPI"
   - Upload the echo-api.json file

## Development
The server is built using Python's http.server module and includes:

- Decorator-based endpoint registration
- Automatic OpenAPI specification generation
- Comprehensive error handling
- Request logging for debugging

## Docker

The Echo Server uses Chainguard's Wolfi-based Python images for enhanced security and minimal attack surface.

### Security Features

- Based on Wolfi, a Linux undistro designed for containers
- Uses Chainguard's hardened Python images with:
  - Minimal base image with only required components
  - Regular security updates and patches
  - Built with security-focused toolchain
  - Signed and verified packages
- Multi-stage build reduces attack surface
- No development dependencies in final image
- Uses virtual environment for isolation
- No Python cache files included
- Minimal runtime dependencies

### Build, Push and Run

1. Build the Docker image:
```bash
docker build -t juerg/echo-server:v1 .
 ```
2. Push the image to Docker Hub:
```bash
docker push juerg/echo-server:v1
 ```
3. Run the container:
```bash
docker run -p 8080:8080 juerg/echo-server:v1
 ```

### Security Scanning with Docker Scout

1. Enable Docker Scout for your repository:
```bash
docker scout enroll
 ```
2. Enable the repository for scanning:
```bash
docker scout repo enable --org juerg juerg/echo-server:v1
 ```
3. Scan for vulnerabilities:
```bash
docker scout cves --only-package express
 ```


Output looks like this:
 ✓ SBOM of image already cached, 50 packages indexed
 ✓ No vulnerable package detected

Overview

                    │       Analyzed Image
────────────────────┼──────────────────────────────
  Target            │
    digest          │  9d5f2ec6b451
    platform        │ linux/arm64
    vulnerabilities │    0C     0H     0M     0L
    size            │ 24 MB
    packages        │ 0

Packages and Vulnerabilities

  No vulnerable packages detected

