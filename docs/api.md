# API Documentation

## Overview

This document describes the API endpoints for your project.

## Authentication

If your project uses authentication, describe it here.

## Endpoints

### Health Check

```
GET /health
```

Returns the health status of the application.

**Response:**
```json
{
    "status": "healthy",
    "version": "1.0.0"
}
```

## Error Handling

All errors return a JSON response with the following structure:

```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable error message"
    }
}
```

## Rate Limiting

If applicable, describe rate limiting policies.
