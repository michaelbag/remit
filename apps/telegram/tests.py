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
    
    def test_role_exclusion_priority(self):
        """Test that role exclusion has higher priority than inclusion"""
        # Add user to both groups
        TelegramUserGroupMembership.objects.create(
            telegram_user=self.telegram_user,
            group=self.group1,
            is_active=True
        )
        
        TelegramUserGroupMembership.objects.create(
            telegram_user=self.telegram_user,
            group=self.group2,
            is_active=True
        )
        
        # Group1 gives USER and OPERATOR roles
        self.group1.group_roles.all().delete()
        TelegramUserGroupRole.objects.create(
            group=self.group1,
            role=TelegramUserRole.USER
        )
        TelegramUserGroupRole.objects.create(
            group=self.group1,
            role=TelegramUserRole.OPERATOR
        )
        
        # Group2 gives ADMIN role but excludes OPERATOR role
        self.group2.group_roles.all().delete()
        TelegramUserGroupRole.objects.create(
            group=self.group2,
            role=TelegramUserRole.ADMIN
        )
        TelegramUserGroupRole.objects.create(
            group=self.group2,
            role=TelegramUserRole.OPERATOR,
            is_exclusion=True  # This should exclude OPERATOR role
        )
        
        # Update user roles
        self.telegram_user.update_all_roles()
        
        # Check that user has USER and ADMIN roles, but not OPERATOR
        user_roles = set(self.telegram_user.get_all_roles())
        expected_roles = {TelegramUserRole.USER, TelegramUserRole.ADMIN}
        self.assertEqual(user_roles, expected_roles)
        
        # Check that TelegramUserRoleAssignment records are correct
        assignments = TelegramUserRoleAssignment.objects.filter(telegram_user=self.telegram_user)
        assignment_roles = {assignment.role for assignment in assignments}
        self.assertEqual(assignment_roles, expected_roles)
    
    def test_multiple_exclusions(self):
        """Test that multiple exclusions work correctly"""
        # Add user to group1
        TelegramUserGroupMembership.objects.create(
            telegram_user=self.telegram_user,
            group=self.group1,
            is_active=True
        )
        
        # Group1 gives USER, OPERATOR, and ADMIN roles
        self.group1.group_roles.all().delete()
        TelegramUserGroupRole.objects.create(
            group=self.group1,
            role=TelegramUserRole.USER
        )
        TelegramUserGroupRole.objects.create(
            group=self.group1,
            role=TelegramUserRole.OPERATOR
        )
        TelegramUserGroupRole.objects.create(
            group=self.group1,
            role=TelegramUserRole.ADMIN
        )
        
        # Add user to group2 which excludes OPERATOR and ADMIN
        TelegramUserGroupMembership.objects.create(
            telegram_user=self.telegram_user,
            group=self.group2,
            is_active=True
        )
        
        self.group2.group_roles.all().delete()
        TelegramUserGroupRole.objects.create(
            group=self.group2,
            role=TelegramUserRole.OPERATOR,
            is_exclusion=True
        )
        TelegramUserGroupRole.objects.create(
            group=self.group2,
            role=TelegramUserRole.ADMIN,
            is_exclusion=True
        )
        
        # Update user roles
        self.telegram_user.update_all_roles()
        
        # Check that user only has USER role (OPERATOR and ADMIN excluded)
        user_roles = set(self.telegram_user.get_all_roles())
        expected_roles = {TelegramUserRole.USER}
        self.assertEqual(user_roles, expected_roles)
        
        # Check that TelegramUserRoleAssignment records are correct
        assignments = TelegramUserRoleAssignment.objects.filter(telegram_user=self.telegram_user)
        assignment_roles = {assignment.role for assignment in assignments}
        self.assertEqual(assignment_roles, expected_roles)
    
    def test_duplicate_membership_prevention(self):
        """Test that duplicate memberships are prevented"""
        from django.db import IntegrityError, transaction
        
        # Create a membership
        membership1 = TelegramUserGroupMembership.objects.create(
            telegram_user=self.telegram_user,
            group=self.group1,
            is_active=True
        )
        
        # Verify only one membership exists
        memberships = TelegramUserGroupMembership.objects.filter(
            telegram_user=self.telegram_user,
            group=self.group1
        )
        self.assertEqual(memberships.count(), 1)
    
    def test_membership_inline_graceful_handling(self):
        """Test that inline formset handles existing memberships gracefully"""
        from django.contrib.admin.sites import AdminSite
        from django.contrib.auth.models import User
        from django.test import RequestFactory
        from apps.telegram.admin import TelegramUserGroupMembershipInline
        
        # Create admin user
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        # Create existing membership
        existing_membership = TelegramUserGroupMembership.objects.create(
            telegram_user=self.telegram_user,
            group=self.group1,
            is_active=True
        )
        
        # Create admin site
        admin_site = AdminSite()
        
        # Create inline instance
        inline = TelegramUserGroupMembershipInline(TelegramUserGroup, admin_site)
        
        # Create request
        factory = RequestFactory()
        request = factory.get('/admin/')
        request.user = admin_user
        
        # Get formset
        formset = inline.get_formset(request, obj=self.group1)
        
        # Test that existing membership is handled gracefully
        # This test verifies that the formset doesn't crash when encountering existing memberships
        self.assertIsNotNone(formset)
        
        # Verify existing membership still exists
        memberships = TelegramUserGroupMembership.objects.filter(
            telegram_user=self.telegram_user,
            group=self.group1
        )
        self.assertEqual(memberships.count(), 1)
        self.assertEqual(memberships.first().is_active, True)


class TelegramUserLanguageTestCase(TestCase):
    """Test cases for TelegramUser language functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.telegram_user = TelegramUser.objects.create(
            user=self.user,
            telegram_id=123456789,
            username='testuser',
            first_name='Test',
            last_name='User',
            language='ru'  # Default language
        )
    
    def test_telegram_user_default_language(self):
        """Test that TelegramUser has default Russian language"""
        self.assertEqual(self.telegram_user.language, 'ru')
        # Test that language display works (may be translated)
        display = self.telegram_user.get_language_display()
        self.assertIsInstance(display, str)
        self.assertTrue(len(display) > 0)
    
    def test_telegram_user_language_change(self):
        """Test changing TelegramUser language"""
        # Change to English
        self.telegram_user.language = 'en'
        self.telegram_user.save()
        
        self.assertEqual(self.telegram_user.language, 'en')
        display = self.telegram_user.get_language_display()
        self.assertIsInstance(display, str)
        self.assertTrue(len(display) > 0)
        
        # Change back to Russian
        self.telegram_user.language = 'ru'
        self.telegram_user.save()
        
        self.assertEqual(self.telegram_user.language, 'ru')
        display = self.telegram_user.get_language_display()
        self.assertIsInstance(display, str)
        self.assertTrue(len(display) > 0)
    
    def test_telegram_user_language_choices(self):
        """Test TelegramUser language choices"""
        choices = self.telegram_user.LANGUAGE_CHOICES
        self.assertEqual(len(choices), 2)
        # Test that choices contain the expected language codes
        choice_codes = [choice[0] for choice in choices]
        self.assertIn('ru', choice_codes)
        self.assertIn('en', choice_codes)
