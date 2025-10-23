# GitHub Issue: Convert TelegramBroadcast to inherit from Catalog

## Issue Title
```
Convert TelegramBroadcast to inherit from Catalog for standardized data management
```

## Description

### Overview
The `TelegramBroadcast` model currently inherits from `models.Model` but should be converted to inherit from `Catalog` to provide standardized data management features including automatic code generation, GUID-based primary keys, and consistent field structure across the application.

### Current State
- `TelegramBroadcast` inherits from `models.Model`
- Has custom fields: `name`, `code`, `title`, `message`, etc.
- Uses integer `id` as primary key
- Manual code generation in `save()` method
- Inconsistent with other catalog-based models in the system

### Requirements

#### 1. Model Inheritance Change
Convert `TelegramBroadcast` from `models.Model` to `Catalog`:

**Current:**
```python
class TelegramBroadcast(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Broadcast Title'))
    name = models.CharField(max_length=32, blank=True, db_index=True, verbose_name=_('Name'))
    code = models.CharField(max_length=9, blank=True, db_index=True, verbose_name=_('Code'))
    message = models.TextField(verbose_name=_('Message Content'))
    # ... other fields
```

**Target:**
```python
class TelegramBroadcast(Catalog):
    title = models.CharField(max_length=200, verbose_name=_('Broadcast Title'))
    message = models.TextField(verbose_name=_('Message Content'))
    # ... other fields
    # name, code, guid, created, modified, delete_mark inherited from Catalog
```

#### 2. Database Migration Strategy
Create a comprehensive migration to safely convert existing data:

1. **Add Catalog fields** (`guid`, `name`, `code`, `delete_mark`, `created`, `modified`)
2. **Populate existing data** with appropriate values
3. **Remove duplicate fields** that are now inherited
4. **Change primary key** from `id` to `guid`
5. **Update foreign key references** in related models

#### 3. Admin Interface Updates
Update `TelegramBroadcastAdmin` to work with `Catalog` inheritance:

- Remove custom `get_list_display()` override
- Use `CatalogAdmin` features properly
- Ensure proper fieldset configuration
- Test all admin functionality

#### 4. Code Generation Integration
Integrate with `Catalog`'s automatic code generation:

- Remove custom `save()` method code generation
- Use `Catalog.next_code` property
- Ensure proper code format and sequence

### Technical Implementation

#### Migration Steps

1. **Create Migration File**
```python
# apps/telegram/migrations/0013_convert_telegrambroadcast_to_catalog.py

def populate_catalog_fields(apps, schema_editor):
    """Populate Catalog fields for existing TelegramBroadcast records"""
    TelegramBroadcast = apps.get_model('telegram', 'TelegramBroadcast')
    
    for broadcast in TelegramBroadcast.objects.all():
        if not broadcast.guid:
            broadcast.guid = str(uuid.uuid4()).replace('-', '')
        if not broadcast.code:
            # Use existing code or generate new one
            broadcast.code = broadcast.code or f'BC{broadcast.id:06d}'
        if not broadcast.name:
            broadcast.name = broadcast.code
        if not broadcast.created:
            broadcast.created = broadcast.created_at
        broadcast.save()

class Migration(migrations.Migration):
    operations = [
        # Add Catalog fields
        migrations.AddField('telegrambroadcast', 'guid', ...),
        migrations.AddField('telegrambroadcast', 'name', ...),
        migrations.AddField('telegrambroadcast', 'code', ...),
        migrations.AddField('telegrambroadcast', 'delete_mark', ...),
        migrations.AddField('telegrambroadcast', 'created', ...),
        migrations.AddField('telegrambroadcast', 'modified', ...),
        
        # Populate data
        migrations.RunPython(populate_catalog_fields),
        
        # Remove old fields and change primary key
        migrations.RemoveField('telegrambroadcast', 'id'),
        migrations.RemoveField('telegrambroadcast', 'name'),  # if duplicate
        migrations.RemoveField('telegrambroadcast', 'code'),  # if duplicate
        migrations.RemoveField('telegrambroadcast', 'created_at'),
        migrations.RemoveField('telegrambroadcast', 'updated_at'),
        
        # Set new primary key
        migrations.AlterField('telegrambroadcast', 'guid', primary_key=True),
    ]
```

2. **Update Model Definition**
```python
class TelegramBroadcast(Catalog):
    """Model for message broadcasts"""
    BROADCAST_STATUS = [
        ('draft', _('Draft')),
        ('scheduled', _('Scheduled')),
        ('sending', _('Sending')),
        ('sent', _('Sent')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
    ]
    
    BROADCAST_TYPE = [
        ('category', _('Category Broadcast')),
        ('individual', _('Individual Message')),
        ('bulk', _('Bulk Message')),
        ('scheduled', _('Scheduled Message')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_('Broadcast Title'))
    message = models.TextField(verbose_name=_('Message Content'))
    broadcast_type = models.CharField(max_length=20, choices=BROADCAST_TYPE, default='category')
    status = models.CharField(max_length=20, choices=BROADCAST_STATUS, default='draft')
    
    # Targeting
    target_categories = models.ManyToManyField(TelegramSubscriptionCategory, blank=True, related_name='broadcasts')
    target_users = models.ManyToManyField(TelegramUser, blank=True, related_name='targeted_broadcasts')
    
    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Scheduled Time'))
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Sent Time'))
    
    # Statistics
    total_recipients = models.IntegerField(default=0, verbose_name=_('Total Recipients'))
    delivered_count = models.IntegerField(default=0, verbose_name=_('Delivered Count'))
    failed_count = models.IntegerField(default=0, verbose_name=_('Failed Count'))
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_broadcasts', verbose_name=_('Created By'))
    
    class Meta:
        verbose_name = _('Telegram Broadcast')
        verbose_name_plural = _('Telegram Broadcasts')
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
```

3. **Update Admin Interface**
```python
@admin.register(TelegramBroadcast)
class TelegramBroadcastAdmin(CatalogAdmin):
    # Remove custom get_list_display override
    # Use CatalogAdmin's automatic field handling
    
    list_display = ['name', 'code', 'title', 'broadcast_type', 'status', 'scheduled_at_display', 'total_recipients', 'delivered_count', 'failed_count', 'created', 'send_broadcast_button']
    list_filter = ['status', 'broadcast_type', 'created', 'scheduled_at']
    search_fields = ['name', 'code', 'title', 'message']
    readonly_fields = ['sent_at', 'total_recipients', 'delivered_count', 'failed_count']
    filter_horizontal = ['target_categories', 'target_users']
    
    # Remove custom get_list_display method
    # Let CatalogAdmin handle field management
    
    @admin.display(description=_('Scheduled Time'), ordering='scheduled_at')
    def scheduled_at_display(self, obj):
        """Display scheduled time in a readable format"""
        if obj.scheduled_at:
            from django.utils import timezone
            local_time = timezone.localtime(obj.scheduled_at)
            return local_time.strftime('%d.%m.%Y %H:%M')
        return '-'

    @admin.display(description=_('Actions'))
    def send_broadcast_button(self, obj):
        if obj.status in ['draft', 'scheduled']:
            return format_html(
                '<a class="button" href="{}">{}</a>',
                reverse('telegram:admin_send_broadcast', args=[obj.pk]),
                _('Send')
            )
        return '-'
    
    fieldsets = [
        (_('Basic Information'), {
            'fields': [('name', 'code'), 'title', 'message', 'broadcast_type', 'status']
        }),
        (_('Target Audience'), {
            'fields': ['target_categories', 'target_users']
        }),
        (_('Scheduling'), {
            'fields': ['scheduled_at']
        }),
        (_('Statistics'), {
            'fields': ['total_recipients', 'delivered_count', 'failed_count', 'sent_at'],
            'classes': ['collapse']
        }),
        (_('Metadata'), {
            'fields': ['created_by'],
            'classes': ['collapse']
        })
    ]
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
```

#### Benefits of Catalog Inheritance

1. **Standardized Data Management**
   - Consistent GUID-based primary keys
   - Automatic code generation
   - Standardized `name`, `created`, `modified` fields
   - Soft delete capability with `delete_mark`

2. **Admin Interface Consistency**
   - Automatic field management by `CatalogAdmin`
   - Consistent display and filtering
   - Standardized fieldsets and readonly fields

3. **Code Generation**
   - Automatic sequential code generation
   - Consistent code format across models
   - Integration with `CommonCounter` system

4. **Data Integrity**
   - GUID-based references are more stable
   - Better support for distributed systems
   - Consistent audit trail

### Testing Requirements

#### 1. Migration Testing
- [ ] Test migration on development database
- [ ] Verify all existing data is preserved
- [ ] Test rollback capability
- [ ] Verify foreign key relationships

#### 2. Model Testing
- [ ] Test automatic code generation
- [ ] Test GUID generation
- [ ] Test field inheritance
- [ ] Test model methods and properties

#### 3. Admin Interface Testing
- [ ] Test list display functionality
- [ ] Test filtering and searching
- [ ] Test form creation and editing
- [ ] Test broadcast sending functionality

#### 4. Integration Testing
- [ ] Test broadcast creation and sending
- [ ] Test delivery tracking
- [ ] Test scheduled broadcasts
- [ ] Test API endpoints

### Acceptance Criteria

- [ ] `TelegramBroadcast` inherits from `Catalog`
- [ ] Migration successfully converts existing data
- [ ] All existing functionality works correctly
- [ ] Admin interface displays properly
- [ ] Automatic code generation works
- [ ] GUID-based primary keys are used
- [ ] Foreign key relationships are maintained
- [ ] No data loss during migration
- [ ] All tests pass
- [ ] Documentation updated

### Risks and Mitigation

#### 1. Data Loss Risk
**Risk:** Migration might cause data loss
**Mitigation:** 
- Comprehensive backup before migration
- Thorough testing on development environment
- Rollback plan prepared

#### 2. Foreign Key Issues
**Risk:** Changing primary key might break foreign key relationships
**Mitigation:**
- Careful migration planning
- Update all related models
- Test all relationships

#### 3. Admin Interface Issues
**Risk:** Admin interface might not work correctly
**Mitigation:**
- Test all admin functionality
- Update admin configuration
- Verify field display and editing

### Priority
**Medium** - This is a technical improvement that will provide better consistency and maintainability, but is not critical for current functionality.

### Estimated Timeline
2-3 weeks for complete implementation including:
- Migration development and testing: 1 week
- Model and admin updates: 3-4 days
- Testing and validation: 3-4 days
- Documentation and deployment: 2-3 days

### Labels
- `enhancement`
- `telegram-bot`
- `database-migration`
- `catalog-inheritance`
- `refactoring`
- `data-consistency`

### Related Issues
- Current TelegramBroadcast implementation
- Catalog model standardization
- Database migration best practices
- Admin interface consistency

### Notes
- This change will improve long-term maintainability
- Consider impact on existing integrations
- Ensure backward compatibility where possible
- Plan for potential API changes if needed
- **Performance**: GUID-based primary keys may have slight performance impact
- **Compatibility**: Ensure all existing code works with new structure
- **Testing**: Comprehensive testing is critical due to data migration complexity
