from django.test import TestCase
from django.contrib.auth.models import User
from .models import (
    TelegramUser, TelegramUserGroup, TelegramUserGroupMembership, 
    TelegramUserGroupRole, TelegramUserRole, TelegramUserRoleAssignment
)


class TelegramUserRoleUpdateTestCase(TestCase):
    """Test case for TelegramUser.update_all_roles() method"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create Telegram user
        self.telegram_user = TelegramUser.objects.create(
            user=self.user,
            telegram_id=123456789,
            username='testuser',
            first_name='Test',
            last_name='User'
        )
        
        # Create test groups
        self.group1 = TelegramUserGroup.objects.create(
            name='Test Group 1',
            description='First test group'
        )
        
        self.group2 = TelegramUserGroup.objects.create(
            name='Test Group 2', 
            description='Second test group'
        )
        
        # Create group roles
        self.group1_role1 = TelegramUserGroupRole.objects.create(
            group=self.group1,
            role=TelegramUserRole.USER
        )
        
        self.group1_role2 = TelegramUserGroupRole.objects.create(
            group=self.group1,
            role=TelegramUserRole.OPERATOR
        )
        
        self.group2_role1 = TelegramUserGroupRole.objects.create(
            group=self.group2,
            role=TelegramUserRole.ADMIN
        )
    
    def test_update_all_roles_single_group(self):
        """Test updating roles when user is member of single group"""
        # Create membership for group1
        membership = TelegramUserGroupMembership.objects.create(
            telegram_user=self.telegram_user,
            group=self.group1
        )
        
        # Update roles
        roles = self.telegram_user.update_all_roles()
        
        # Check that roles are updated correctly
        expected_roles = [TelegramUserRole.USER, TelegramUserRole.OPERATOR]
        self.assertEqual(sorted(roles), sorted(expected_roles))
        
        # Check that role assignments are created in database
        role_assignments = self.telegram_user.user_roles.filter(is_active=True)
        assigned_roles = [ra.role for ra in role_assignments]
        self.assertEqual(sorted(assigned_roles), sorted(expected_roles))
    
    def test_update_all_roles_multiple_groups(self):
        """Test updating roles when user is member of multiple groups"""
        # Create memberships for both groups
        TelegramUserGroupMembership.objects.create(
            telegram_user=self.telegram_user,
            group=self.group1
        )
        
        TelegramUserGroupMembership.objects.create(
            telegram_user=self.telegram_user,
            group=self.group2
        )
        
        # Update roles
        roles = self.telegram_user.update_all_roles()
        
        # Check that roles from all groups are included
        expected_roles = [
            TelegramUserRole.USER, 
            TelegramUserRole.OPERATOR, 
            TelegramUserRole.ADMIN
        ]
        self.assertEqual(sorted(roles), sorted(expected_roles))
        
        # Check that role assignments are created in database
        role_assignments = self.telegram_user.user_roles.filter(is_active=True)
        assigned_roles = [ra.role for ra in role_assignments]
        self.assertEqual(sorted(assigned_roles), sorted(expected_roles))
    
    def test_update_all_roles_inactive_membership(self):
        """Test that inactive memberships are not included"""
        # Create active membership
        TelegramUserGroupMembership.objects.create(
            telegram_user=self.telegram_user,
            group=self.group1
        )
        
        # Create inactive membership
        TelegramUserGroupMembership.objects.create(
            telegram_user=self.telegram_user,
            group=self.group2,
            is_active=False
        )
        
        # Update roles
        roles = self.telegram_user.update_all_roles()
        
        # Check that only active membership roles are included
        expected_roles = [TelegramUserRole.USER, TelegramUserRole.OPERATOR]
        self.assertEqual(sorted(roles), sorted(expected_roles))
        
        # Check that role assignments are created in database
        role_assignments = self.telegram_user.user_roles.filter(is_active=True)
        assigned_roles = [ra.role for ra in role_assignments]
        self.assertEqual(sorted(assigned_roles), sorted(expected_roles))
    
    def test_update_all_roles_inactive_group_role(self):
        """Test that inactive group roles are not included"""
        # Create membership
        TelegramUserGroupMembership.objects.create(
            telegram_user=self.telegram_user,
            group=self.group1
        )
        
        # Deactivate one group role
        self.group1_role2.is_active = False
        self.group1_role2.save()
        
        # Update roles
        roles = self.telegram_user.update_all_roles()
        
        # Check that only active group roles are included
        expected_roles = [TelegramUserRole.USER]
        self.assertEqual(sorted(roles), sorted(expected_roles))
        
        # Check that role assignments are created in database
        role_assignments = self.telegram_user.user_roles.filter(is_active=True)
        assigned_roles = [ra.role for ra in role_assignments]
        self.assertEqual(sorted(assigned_roles), sorted(expected_roles))
    
    def test_get_all_roles_auto_update(self):
        """Test that get_all_roles() automatically updates roles if no role assignments exist"""
        # Create membership
        TelegramUserGroupMembership.objects.create(
            telegram_user=self.telegram_user,
            group=self.group1
        )
        
        # Ensure no role assignments exist
        self.telegram_user.user_roles.all().delete()
        
        # Call get_all_roles() - should auto-update
        roles = self.telegram_user.get_all_roles()
        
        # Check that roles are updated
        expected_roles = [TelegramUserRole.USER, TelegramUserRole.OPERATOR]
        self.assertEqual(sorted(roles), sorted(expected_roles))
        
        # Check that role assignments are created in database
        role_assignments = self.telegram_user.user_roles.filter(is_active=True)
        assigned_roles = [ra.role for ra in role_assignments]
        self.assertEqual(sorted(assigned_roles), sorted(expected_roles))
    
    def test_group_save_updates_members_roles(self):
        """Test that saving a group updates roles for all its members"""
        # Create membership
        TelegramUserGroupMembership.objects.create(
            telegram_user=self.telegram_user,
            group=self.group1
        )
        
        # Initially update roles manually
        self.telegram_user.update_all_roles()
        
        # Add a new role to the group
        new_role = TelegramUserGroupRole.objects.create(
            group=self.group1,
            role=TelegramUserRole.ADMIN
        )
        
        # Save the group - this should trigger role updates for all members
        self.group1.save()
        
        # Check that the user now has the new role
        expected_roles = [
            TelegramUserRole.USER, 
            TelegramUserRole.OPERATOR, 
            TelegramUserRole.ADMIN
        ]
        
        role_assignments = self.telegram_user.user_roles.filter(is_active=True)
        assigned_roles = [ra.role for ra in role_assignments]
        self.assertEqual(sorted(assigned_roles), sorted(expected_roles))
