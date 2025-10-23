# GitHub Issue: Add Territory Model and Bidirectional Integration with 1C:Enterprise REMIT System

## Issue Title
```
Add Territory Model and Bidirectional Data Exchange with 1C:Enterprise REMIT System
```

## Description

### Overview
We need to add a "Territory" model to track equipment locations and implement bidirectional data exchange with the 1C:Enterprise REMIT system. Additionally, we need to implement equipment movement operations (for non-virtual equipment) between territories with history tracking and responsible employee identification.

### Current State
- Equipment (`Equipment`) has a relationship with employees (`Employee`) through the `employee` field
- Equipment can be virtual (`virtual = True`) or physical
- `ExtSystem` model exists for external system integration
- No model for territories/equipment locations
- No equipment movement tracking system
- No 1C:Enterprise integration

### Requirements

#### 1. Territory Model
- Create `Territory` model to store territory/location information
- Support hierarchical territory structure (building → floor → room)
- Link to organization (`Organization`)
- Territory archiving capability

#### 2. Equipment-Territory Relationship
- Add `territory` field to `Equipment` model
- Restrict relationship to non-virtual equipment only
- Support location change history

#### 3. Equipment Movement System
- Create `EquipmentMovement` model to track movements
- Preserve complete equipment movement history
- Track responsible employee for each movement
- Movement timestamps
- Movement reason tracking

#### 4. Bidirectional 1C REMIT Integration
- Integration with existing `ExtSystem` framework
- Territory data synchronization
- Equipment movement data synchronization
- Data conflict resolution
- Synchronization operation logging

### Technical Implementation

#### Models to Create/Modify

1. **Territory** (New model)
```python
class Territory(RecursiveCatalog):
    name = models.CharField(max_length=150, blank=True, db_index=True)
    title = models.CharField(max_length=150, blank=True, help_text='Full title for printing')
    organization = models.ForeignKey('org.Organization',
                                   related_name='territories',
                                   null=True,
                                   blank=True,
                                   on_delete=models.SET_NULL)
    address = models.TextField(blank=True, help_text='Territory address')
    description = models.TextField(blank=True, help_text='Territory description')
    archive = models.BooleanField(default=False, db_index=True)
    contact_person = models.ForeignKey('org.Employee',
                                     null=True,
                                     blank=True,
                                     on_delete=models.SET_NULL,
                                     related_name='managed_territories')
    
    class Meta:
        verbose_name = _('Territory')
        verbose_name_plural = _('Territories')
        ordering = ["title", "name", "code"]
```

2. **EquipmentMovement** (New model)
```python
class EquipmentMovement(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    equipment = models.ForeignKey('equipment.Equipment',
                                on_delete=models.CASCADE,
                                related_name='movements')
    from_territory = models.ForeignKey(Territory,
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     blank=True,
                                     related_name='equipment_movements_from')
    to_territory = models.ForeignKey(Territory,
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   blank=True,
                                   related_name='equipment_movements_to')
    moved_by = models.ForeignKey('org.Employee',
                               on_delete=models.SET_NULL,
                               null=True,
                               blank=True,
                               related_name='equipment_movements')
    movement_date = models.DateTimeField(default=timezone.now)
    reason = models.TextField(blank=True, help_text='Movement reason')
    comment = models.TextField(blank=True, help_text='Additional comments')
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Equipment Movement')
        verbose_name_plural = _('Equipment Movements')
        ordering = ['-movement_date']
```

3. **TerritorySyncSession** (New model)
```python
class TerritorySyncSession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    external_system = models.ForeignKey('config.ExtSystem', on_delete=models.CASCADE)
    sync_type = models.CharField(max_length=20, choices=[
        ('full', 'Full Synchronization'),
        ('incremental', 'Incremental Synchronization'),
        ('territories', 'Territory Synchronization'),
        ('movements', 'Movement Synchronization')
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
    
    class Meta:
        verbose_name = _('Territory Sync Session')
        verbose_name_plural = _('Territory Sync Sessions')
```

4. **TerritorySyncLog** (New model)
```python
class TerritorySyncLog(models.Model):
    session = models.ForeignKey(TerritorySyncSession, on_delete=models.CASCADE, related_name='logs')
    territory = models.ForeignKey(Territory, on_delete=models.CASCADE, null=True, blank=True)
    movement = models.ForeignKey(EquipmentMovement, on_delete=models.CASCADE, null=True, blank=True)
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
    
    class Meta:
        verbose_name = _('Territory Sync Log')
        verbose_name_plural = _('Territory Sync Logs')
```

5. **Modify Equipment model**
```python
# Add to existing Equipment model
territory = models.ForeignKey(Territory,
                            null=True,
                            blank=True,
                            on_delete=models.SET_NULL,
                            related_name='equipments',
                            limit_choices_to={'archive': False, 'delete_mark': False})
last_sync_datetime = models.DateTimeField(null=True, blank=True)
sync_status = models.CharField(max_length=20, choices=[
    ('synced', 'Synchronized'),
    ('pending', 'Pending Sync'),
    ('conflict', 'Conflict Detected'),
    ('error', 'Sync Error')
], default='pending')
external_system_id = models.CharField(max_length=100, blank=True)  # ID in 1C system
```

6. **Modify Territory model** (Add sync fields)
```python
# Add to Territory model
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

1. **Territory Management Endpoints**
```python
# GET /api/territories/
# POST /api/territories/
# GET /api/territories/<id>/
# PUT /api/territories/<id>/
# DELETE /api/territories/<id>/
# GET /api/territories/<id>/equipment/
```

2. **Equipment Movement Endpoints**
```python
# GET /api/equipment-movements/
# POST /api/equipment-movements/
# GET /api/equipment-movements/<id>/
# GET /api/equipment/<id>/movements/
# POST /api/equipment/<id>/move/
```

3. **1C Integration Endpoints**
```python
# POST /api/territory-sync/start-session/
# POST /api/territory-sync/end-session/
# GET /api/territory-sync/session-status/<session_id>/
# POST /api/territory-sync/sync-territories/
# POST /api/territory-sync/sync-movements/
# GET /api/territory-sync/conflicts/
# POST /api/territory-sync/resolve-conflict/
```

#### Synchronization Service

1. **TerritorySyncService** (New service class)
```python
class TerritorySyncService:
    def start_sync_session(self, external_system, sync_type='incremental')
    def sync_territories(self, session_id, territories_data)
    def sync_movements(self, session_id, movements_data)
    def detect_conflicts(self, local_data, external_data)
    def resolve_conflict(self, conflict_id, resolution)
    def rollback_session(self, session_id)
    def get_sync_status(self, session_id)
    def get_territory_hierarchy(self)
    def get_equipment_movements_since(self, since_datetime)
```

#### 1C:Enterprise Integration

1. **Data Format Specification for Territories**
```json
{
    "session_id": "uuid",
    "sync_type": "incremental|full|territories",
    "last_sync_datetime": "2024-01-01T00:00:00Z",
    "territories": [
        {
            "external_id": "1c_territory_id",
            "name": "Main Office",
            "title": "Company Main Office",
            "parent_external_id": "1c_parent_territory_id",
            "organization_external_id": "1c_organization_id",
            "address": "123 Example Street, Building 1",
            "description": "Main company building",
            "contact_person_external_id": "1c_employee_id",
            "archive": false,
            "last_modified": "2024-01-01T12:00:00Z"
        }
    ]
}
```

2. **Data Format Specification for Equipment Movements**
```json
{
    "session_id": "uuid",
    "sync_type": "movements",
    "last_sync_datetime": "2024-01-01T00:00:00Z",
    "movements": [
        {
            "external_id": "1c_movement_id",
            "equipment_external_id": "1c_equipment_id",
            "from_territory_external_id": "1c_from_territory_id",
            "to_territory_external_id": "1c_to_territory_id",
            "moved_by_external_id": "1c_employee_id",
            "movement_date": "2024-01-01T10:00:00Z",
            "reason": "Relocation to new office",
            "comment": "Planned equipment relocation",
            "last_modified": "2024-01-01T12:00:00Z"
        }
    ]
}
```

3. **Response Format**
```json
{
    "session_id": "uuid",
    "status": "completed|failed|partial",
    "processed_count": 100,
    "successful_count": 95,
    "failed_count": 5,
    "conflicts": [
        {
            "territory_id": "uuid",
            "conflict_type": "data_mismatch|timestamp_conflict",
            "local_data": {...},
            "external_data": {...}
        }
    ],
    "errors": [
        {
            "territory_id": "uuid",
            "error_message": "Validation failed"
        }
    ]
}
```

### Business Logic

#### Equipment Movement Rules
1. Only non-virtual equipment can be moved
2. Equipment movement creates `EquipmentMovement` record
3. Updates `territory` field in `Equipment` model
4. All movements are logged with responsible employee
5. Support for bulk equipment movement

#### Territory Hierarchy
1. Support hierarchical structure (building → floor → room)
2. Property inheritance from parent territories
3. Hierarchy validation
4. Support for territory relocation within hierarchy

### Admin Interface

1. **Territory Admin**
- Hierarchical territory display
- Organization filtering
- Search by name and address
- Archive management

2. **Equipment Movement Admin**
- Movement history display
- Filter by equipment, territory, employee
- Search by date and reason
- Movement history export

3. **Sync Session Admin**
- Synchronization session monitoring
- Sync log viewing
- Conflict management
- Synchronization statistics

### Security and Authentication

1. **API Authentication**
- Token-based authentication for 1C system
- IP whitelist for sync endpoints
- Rate limiting for sync operations

2. **Data Validation**
- Input validation for sync data
- Business rule validation
- Data integrity checks

### Monitoring and Logging

1. **Sync Monitoring**
- Real-time sync status dashboard
- Synchronization performance metrics
- Error rate monitoring

2. **Audit Trail**
- Complete audit log of all sync operations
- Data change tracking
- User action logging

### Acceptance Criteria

- [ ] `Territory` model created with hierarchy support
- [ ] `EquipmentMovement` model for movement tracking
- [ ] `TerritorySyncSession` and `TerritorySyncLog` models for synchronization
- [ ] `territory` field added to `Equipment` model
- [ ] API endpoints for territory and movement management
- [ ] API endpoints for 1C synchronization
- [ ] `TerritorySyncService` for sync processing
- [ ] Conflict detection and resolution system
- [ ] Session management and rollback capability
- [ ] Data format specification for 1C integration
- [ ] Authentication and security measures
- [ ] Comprehensive error handling and logging
- [ ] Unit tests for sync functionality
- [ ] Integration tests with mock 1C system
- [ ] Documentation for 1C integration
- [ ] Admin interface for sync monitoring
- [ ] Business rule validation for equipment movement
- [ ] Bulk movement operation support

### Priority
**High** - This is a critical functionality for physical equipment management and integration with the corporate 1C system.

### Estimated Timeline
6-8 weeks for complete implementation including testing, documentation, and 1C integration.

### Labels
- `enhancement`
- `integration`
- `1c-enterprise`
- `territory-management`
- `equipment-movement`
- `synchronization`
- `api`

### Related Issues
- Current equipment management system
- External system integration framework
- API authentication system

### Notes
- Implementation should be backward compatible with existing equipment
- Consider phased sync implementation (basic sync first, then advanced conflict resolution)
- Ensure proper error handling for network issues and system downtime
- Plan data migration strategy for existing equipment
- Consider implementing sync queue for high-volume scenarios
- **Physical Equipment Management**: Only non-virtual equipment can be assigned to territories and moved
- **Movement History**: All equipment movements must be preserved with responsible employee and movement reason
- **Territory Hierarchy**: Support multi-level territory structure (building → floor → room) for detailed equipment location management
