# API Documentation

## QR Codes API

### Get Modified QR Codes Count

**Endpoint**: `GET /api/qr-codes/modified-count/`

**Description**: Returns the count of QR codes that have been modified since a specific datetime.

**Authentication**: Required (Token Authentication)

**Parameters**:
- `since` (required, string): ISO 8601 datetime string

**Example Request**:
```bash
curl -X GET "https://test2.p7e.ru/api/qr-codes/modified-count/?since=2024-01-01T00:00:00Z" \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -k
```

**Example Response** (200 OK):
```json
{
    "count": 5,
    "since": "2024-01-01T00:00:00+00:00",
    "message": "Found 5 QR codes modified since 2024-01-01T00:00:00+00:00"
}
```

**Supported DateTime Formats**:
- `2024-01-01T00:00:00Z`
- `2024-01-01T00:00:00+00:00`
- `2024-01-01 00:00:00`

**Error Responses**:

**400 Bad Request** - Missing or invalid `since` parameter:
```json
{
    "error": "Parameter \"since\" is required. Format: ISO datetime string"
}
```

**400 Bad Request** - Invalid datetime format:
```json
{
    "error": "Invalid datetime format. Use ISO format: [error details]"
}
```

**403 Forbidden** - Authentication required:
```json
{
    "detail": "Учетные данные не были предоставлены."
}
```

**Use Cases**:
- Monitor QR code modifications for synchronization purposes
- Track changes since last update
- Generate reports on QR code activity
- Integration with external systems for data synchronization

**Implementation Details**:
- Uses Django's `modified` field from the base GUIDModel
- Supports timezone-aware datetime comparisons
- Efficient database query with proper indexing
- Comprehensive input validation and error handling
