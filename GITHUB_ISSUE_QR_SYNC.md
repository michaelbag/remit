# GitHub Issue: Implement Bidirectional QR Code Synchronization with 1C:Enterprise REMIT

## Issue Title
```
Implement Bidirectional QR Code Synchronization with 1C:Enterprise REMIT System
```

## Description

### Overview
Currently, the REMIT system manages QR codes independently without synchronization with external systems. We need to implement a comprehensive bidirectional synchronization mechanism between the current REMIT Django system and the 1C:Enterprise REMIT configuration to ensure data consistency and real-time updates of QR code states and bindings.

### Current State
- QR codes are managed locally in the Django system
- QR codes can be linked to Equipment, Resources, or Services
- QR codes are linked to Operations that control user access to perform operations on linked objects
- QR codes serve as access control mechanisms - users can perform operations on equipment, services (programs), or resources based on the operations associated with the QR code
- QR codes have states: `archive`, `fixed`, and various binding states
- No synchronization mechanism exists with external systems
- External system tracking exists (`ExtSystem` model) but is not utilized for QR code sync

### Requirements

#### 1. Bidirectional Synchronization
- **1C:Enterprise REMIT** will be the **initiator** of synchronization
- Django REMIT system will act as a **responder** to sync requests
- Support for both **push** and **pull** synchronization modes
- Conflict resolution for simultaneous updates

#### 2. QR Code State Synchronization
Synchronize the following QR code attributes:
- **Basic Properties**: `title`, `name`, `archive`, `fixed`
- **Bindings**: `equipment`, `resource`, `service` relationships
- **Operations**: `operations` many-to-many relationships that control user access to operations on linked objects
- **User Access Control**: Operations linked to QR codes determine which users can perform specific operations on the associated equipment, services (programs), or resources
- **Metadata**: `created_at`, `modified` timestamps
- **QR Properties**: `guid_public_code`, `short_public_code`, `url`

#### 3. Timestamp-Based Conflict Resolution
- Track `last_sync_datetime` for each QR code
- Track `last_modified_datetime` in both systems
- Implement "last-write-wins" conflict resolution
- Support for manual conflict resolution for critical data

#### 4. Session Management
- Track synchronization sessions with unique identifiers
- Log all synchronization activities
- Support for partial synchronization (incremental updates)
- Rollback capability for failed synchronization sessions

### Technical Implementation

#### Models to Create/Modify

1. **QRCodeSyncSession** (New model)
```python
class QRCodeSyncSession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    external_system = models.ForeignKey('config.ExtSystem', on_delete=models.CASCADE)
    sync_type = models.CharField(max_length=20, choices=[
        ('full', 'Full Synchronization'),
        ('incremental', 'Incremental Synchronization'),
        ('push', 'Push to External'),
        ('pull', 'Pull from External')
    ])
    status = models.CharField(max_length=20, choices=[
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('rolled_back', 'Rolled Back')
    ])
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_sync_datetime = models.DateTimeField(null=True, blank=True)
    records_processed = models.IntegerField(default=0)
    records_successful = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    error_log = models.JSONField(default=list, blank=True)
```

2. **QRCodeSyncLog** (New model)
```python
class QRCodeSyncLog(models.Model):
    session = models.ForeignKey(QRCodeSyncSession, on_delete=models.CASCADE, related_name='logs')
    qr_code = models.ForeignKey('qr.QRCode', on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=[
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('conflict', 'Conflict Detected'),
        ('skipped', 'Skipped')
    ])
    external_data = models.JSONField(default=dict, blank=True)
    local_data = models.JSONField(default=dict, blank=True)
    conflict_resolution = models.CharField(max_length=20, choices=[
        ('external_wins', 'External System Wins'),
        ('local_wins', 'Local System Wins'),
        ('manual', 'Manual Resolution Required')
    ], null=True, blank=True)
    processed_at = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(blank=True)
```

3. **Modify QRCode model**
```python
# Add to existing QRCode model
last_sync_datetime = models.DateTimeField(null=True, blank=True)
sync_status = models.CharField(max_length=20, choices=[
    ('synced', 'Synchronized'),
    ('pending', 'Pending Sync'),
    ('conflict', 'Conflict Detected'),
    ('error', 'Sync Error')
], default='pending')
external_system_id = models.CharField(max_length=100, blank=True)  # ID in 1C system
```

#### API Endpoints to Create

1. **Synchronization Endpoints**
```python
# POST /api/qr-sync/start-session/
# POST /api/qr-sync/end-session/
# GET /api/qr-sync/session-status/<session_id>/
# POST /api/qr-sync/sync-qr-codes/
# GET /api/qr-sync/conflicts/
# POST /api/qr-sync/resolve-conflict/
```

2. **Data Exchange Endpoints**
```python
# GET /api/qr-codes/sync-data/?since=<datetime>&limit=<count>
# POST /api/qr-codes/bulk-update/
# GET /api/qr-codes/conflict-data/<qr_code_id>/
```

#### Synchronization Service

1. **QRCodeSyncService** (New service class)
```python
class QRCodeSyncService:
    def start_sync_session(self, external_system, sync_type='incremental')
    def sync_qr_codes(self, session_id, qr_codes_data)
    def detect_conflicts(self, local_qr, external_qr)
    def resolve_conflict(self, conflict_id, resolution)
    def rollback_session(self, session_id)
    def get_sync_status(self, session_id)
```

#### 1C:Enterprise Integration

1. **Data Format Specification**
```json
{
    "session_id": "uuid",
    "sync_type": "incremental|full",
    "last_sync_datetime": "2024-01-01T00:00:00Z",
    "qr_codes": [
        {
            "external_id": "1c_system_id",
            "guid_public_code": "uuid",
            "title": "QR Code Title",
            "archive": false,
            "fixed": false,
            "equipment_id": "equipment_external_id",
            "resource_id": "resource_external_id", 
            "service_id": "service_external_id",
            "operations": ["operation_id1", "operation_id2"],
            "user_access_operations": {
                "equipment_operations": ["view", "maintain", "repair"],
                "service_operations": ["install", "configure", "update"],
                "resource_operations": ["allocate", "deallocate", "monitor"]
            },
            "last_modified": "2024-01-01T12:00:00Z"
        }
    ]
}
```

2. **Response Format**
```json
{
    "session_id": "uuid",
    "status": "completed|failed|partial",
    "processed_count": 100,
    "successful_count": 95,
    "failed_count": 5,
    "conflicts": [
        {
            "qr_code_id": "uuid",
            "conflict_type": "data_mismatch|timestamp_conflict",
            "local_data": {...},
            "external_data": {...}
        }
    ],
    "errors": [
        {
            "qr_code_id": "uuid",
            "error_message": "Validation failed"
        }
    ]
}
```

### Synchronization Flow

#### 1. Session Initialization
1. 1C system initiates sync session
2. Django system creates `QRCodeSyncSession` record
3. Returns session ID and current sync status

#### 2. Data Exchange
1. 1C system sends QR codes data with timestamps
2. Django system processes each QR code:
   - Check for conflicts based on timestamps
   - Apply updates or mark conflicts
   - Log all operations

#### 3. Conflict Resolution
1. Django system identifies conflicts
2. Returns conflict list to 1C system
3. 1C system resolves conflicts or requests manual resolution
4. Django system applies resolutions

#### 4. Session Completion
1. Django system finalizes session
2. Updates `last_sync_datetime` for all processed QR codes
3. Returns final status and statistics

### Security and Authentication

1. **API Authentication**
   - Token-based authentication for 1C system
   - IP whitelist for sync endpoints
   - Rate limiting for sync operations

2. **Data Validation**
   - Input validation for all sync data
   - Business rule validation
   - Data integrity checks

### Monitoring and Logging

1. **Sync Monitoring**
   - Real-time sync status dashboard
   - Sync performance metrics
   - Error rate monitoring

2. **Audit Trail**
   - Complete audit log of all sync operations
   - Data change tracking
   - User action logging

### Acceptance Criteria

- [ ] `QRCodeSyncSession` and `QRCodeSyncLog` models implemented
- [ ] QRCode model extended with sync fields
- [ ] Synchronization API endpoints created
- [ ] `QRCodeSyncService` service class implemented
- [ ] Conflict detection and resolution system
- [ ] Session management and rollback capability
- [ ] Data format specification for 1C integration
- [ ] Authentication and security measures
- [ ] Comprehensive error handling and logging
- [ ] Unit tests for sync functionality
- [ ] Integration tests with mock 1C system
- [ ] Documentation for 1C integration
- [ ] Admin interface for sync monitoring

### Priority
**High** - This is a critical integration feature that will ensure data consistency between systems and enable real-time updates.

### Estimated Timeline
4-6 weeks for complete implementation including testing, documentation, and 1C integration.

### Labels
- `enhancement`
- `integration`
- `1c-enterprise`
- `qr-codes`
- `synchronization`
- `api`

### Related Issues
- Current QR code management system
- External system integration framework
- API authentication system

### Notes
- This implementation should be backward compatible with existing QR codes
- Consider implementing sync in phases (basic sync first, then advanced conflict resolution)
- Ensure proper error handling for network issues and system downtime
- Plan for data migration strategy for existing QR codes
- Consider implementing sync queue for high-volume scenarios
- **Access Control Integration**: QR codes serve as access control mechanisms - when users scan a QR code, they gain access to perform specific operations on the linked equipment, services, or resources based on the operations associated with that QR code
- **Operation-Based Permissions**: The synchronization must preserve the relationship between QR codes and operations, as this determines what actions users can perform when accessing the linked objects
