# GitHub Issue: Implement Role-Based Access Control for Telegram Bot

## Issue Title
```
Implement Role-Based Access Control (RBAC) for Telegram Bot Operations
```

## Description

### Overview
Currently, the Telegram bot has basic user authentication through phone number verification and employee linking. We need to implement a comprehensive role-based access control system to manage different levels of access and permissions for Telegram bot operations.

### Current State
- Telegram users are linked to employees via phone number verification
- Basic command handling exists (`/start`, `/help`, `/status`, `/equipment`)
- No role-based restrictions on bot functionality
- All authenticated users have the same level of access

### Requirements

#### 1. Fixed Role System
Create a predefined set of roles (not a dynamic model) for Telegram bot operations:

**Proposed Roles:**
- `VIEWER` - Can view equipment and basic information
- `USER` - Can view and request equipment operations
- `OPERATOR` - Can perform equipment management operations
- `ADMIN` - Full administrative access to bot functions
- `SUPER_ADMIN` - System-wide administrative access

#### 2. User Groups Management
- Create `TelegramUserGroup` model to manage groups of Telegram users
- Each group should have a predefined set of roles
- Allow adding/removing Telegram users to/from groups
- Support multiple groups per user (role inheritance/combination)

#### 3. Permission System
- Implement permission checking for each bot command/operation
- Role-based access control for different bot functionalities
- Audit logging for role-based actions

### Technical Implementation

#### Models to Create/Modify

1. **TelegramUserRole** (Fixed roles enum/choices)
```python
class TelegramUserRole(models.TextChoices):
    VIEWER = 'viewer', 'Viewer'
    USER = 'user', 'User' 
    OPERATOR = 'operator', 'Operator'
    ADMIN = 'admin', 'Admin'
    SUPER_ADMIN = 'super_admin', 'Super Admin'
```

2. **TelegramUserGroup** (New model)
```python
class TelegramUserGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    roles = models.JSONField(default=list)  # List of allowed roles
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

3. **TelegramUserGroupMembership** (New model)
```python
class TelegramUserGroupMembership(models.Model):
    telegram_user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    group = models.ForeignKey(TelegramUserGroup, on_delete=models.CASCADE)
    assigned_roles = models.JSONField(default=list)  # Roles assigned to this user in this group
    is_active = models.BooleanField(default=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
```

4. **Modify TelegramUser model**
- Add methods for role checking
- Add methods for permission validation

#### Bot Integration
- Modify `TelegramBot` class to check permissions before executing commands
- Add role-based command filtering
- Implement permission decorators for command handlers

#### Admin Interface
- Add admin interface for managing user groups
- Add interface for assigning users to groups with specific roles
- Add role management interface

### Acceptance Criteria

- [ ] Fixed role system implemented with predefined roles
- [ ] TelegramUserGroup model created with role assignment capability
- [ ] TelegramUserGroupMembership model for user-group relationships
- [ ] Permission checking system integrated into bot command handlers
- [ ] Admin interface for managing groups and user assignments
- [ ] Role-based access control working for all bot commands
- [ ] Audit logging for role-based actions
- [ ] Unit tests for role and permission system
- [ ] Documentation for role management

### Priority
**Medium** - This is an important security and access control enhancement that will improve the bot's functionality and security.

### Estimated Timeline
2-3 weeks for complete implementation including testing and documentation.

### Labels
- `enhancement`
- `security` 
- `telegram-bot`
- `rbac`
- `access-control`

### Related Issues
- Current Telegram bot implementation
- Employee management system
- Equipment management system

### Notes
- This implementation should be backward compatible with existing Telegram users
- Consider migration strategy for existing users (default role assignment)
- Ensure role system is extensible for future requirements
- Consider integration with existing Django permission system if applicable
