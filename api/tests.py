from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
import apps.qr.models as qr_models
from datetime import datetime, timedelta


class QRCodeModifiedCountAPITest(APITestCase):
    def setUp(self):
        """Set up test data"""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create a test QR type
        self.qr_type = qr_models.QRType.objects.create(
            name='Test QR Type',
            url_root='https://example.com'
        )
        
        # Create test QR codes with different modification times
        self.qr_code_old = qr_models.QRCode.objects.create(
            title='Old QR Code',
            qr_type=self.qr_type,
            short_public_code='OLD123'
        )
        
        self.qr_code_recent = qr_models.QRCode.objects.create(
            title='Recent QR Code',
            qr_type=self.qr_type,
            short_public_code='RECENT123'
        )
        
        # Manually set modification time for old QR code to be older
        old_time = timezone.now() - timedelta(days=10)
        qr_models.QRCode.objects.filter(pk=self.qr_code_old.pk).update(modified=old_time)
        
        # Recent QR code should have current modification time
        recent_time = timezone.now() - timedelta(hours=1)
        qr_models.QRCode.objects.filter(pk=self.qr_code_recent.pk).update(modified=recent_time)
    
    def test_qr_codes_modified_count_without_auth(self):
        """Test that endpoint requires authentication"""
        url = reverse('qr_codes_modified_count')
        response = self.client.get(url, {'since': '2024-01-01T00:00:00Z'})
        # Django REST Framework returns 403 Forbidden for unauthenticated requests
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_qr_codes_modified_count_missing_since_param(self):
        """Test that endpoint requires 'since' parameter"""
        self.client.force_authenticate(user=self.user)
        url = reverse('qr_codes_modified_count')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('since', response.data['error'])
    
    def test_qr_codes_modified_count_invalid_datetime(self):
        """Test endpoint with invalid datetime format"""
        self.client.force_authenticate(user=self.user)
        url = reverse('qr_codes_modified_count')
        response = self.client.get(url, {'since': 'invalid-datetime'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid datetime format', response.data['error'])
    
    def test_qr_codes_modified_count_valid_request(self):
        """Test endpoint with valid datetime parameter"""
        self.client.force_authenticate(user=self.user)
        url = reverse('qr_codes_modified_count')
        
        # Test with datetime from 2 days ago (should include recent QR code)
        since_datetime = timezone.now() - timedelta(days=2)
        response = self.client.get(url, {'since': since_datetime.isoformat()})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('since', response.data)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['count'], 1)  # Only recent QR code
    
    def test_qr_codes_modified_count_old_datetime(self):
        """Test endpoint with very old datetime (should include all QR codes)"""
        self.client.force_authenticate(user=self.user)
        url = reverse('qr_codes_modified_count')
        
        # Test with datetime from 1 year ago (should include all QR codes)
        since_datetime = timezone.now() - timedelta(days=365)
        response = self.client.get(url, {'since': since_datetime.isoformat()})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # Both QR codes
    
    def test_qr_codes_modified_count_future_datetime(self):
        """Test endpoint with future datetime (should return 0)"""
        self.client.force_authenticate(user=self.user)
        url = reverse('qr_codes_modified_count')
        
        # Test with future datetime (should return 0)
        future_datetime = timezone.now() + timedelta(days=1)
        response = self.client.get(url, {'since': future_datetime.isoformat()})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)  # No QR codes
