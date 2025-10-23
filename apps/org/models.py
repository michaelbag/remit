from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
# from smart_selects.db_fields import ChainedForeignKey

from common import models as common_models
from datetime import date
from django.utils.translation import gettext_lazy as _
import re


class Organization(common_models.Catalog):
    name = models.CharField(max_length=150, blank=True, db_index=True)
    archive = models.BooleanField(default=False, help_text=_('Is archived'), db_index=True)

    class Meta:
        verbose_name = _('Organization')


class Department(common_models.RecursiveCatalogByElements):
    organization = models.ForeignKey(Organization,
                                     related_name='departments',
                                     null=True,
                                     on_delete=models.SET_NULL)
    name = models.CharField(max_length=150, blank=False)
    archive = models.BooleanField(default=False, help_text=_('Is archived'))

    def __str__(self):
        return "%s%s" % (self.name, f" ({self.organization.name})" if self.organization else '')

    class Meta:
        verbose_name = _('Department')


class Employee(common_models.Catalog):
    organization = models.ForeignKey(Organization,
                                     related_name='employees',
                                     null=True,
                                     blank=True,
                                     on_delete=models.SET_NULL)
    department = models.ForeignKey(Department,
                                   null=True,
                                   on_delete=models.SET_NULL,
                                   blank=True,
                                   related_name='employees')
    # department = ChainedForeignKey(Department, null=True,
    #                                on_delete=models.SET_NULL,
    #                                blank=True,
    #                                related_name='employees',
    #                                chained_field='organization',
    #                                chained_model_field='organization',
    #                                show_all=False,
    #                                auto_choose=True,
    #                                sort=True)
    name = models.CharField(max_length=150, blank=False, help_text=_('Full name'), db_index=True)
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        help_text=_('Phone number for Telegram (format: 79161234567 or +79161234567)'), 
        db_index=True,
        validators=[
            RegexValidator(
                regex=r'^(\+?7|8)?[0-9]{10}$',
                message=_('Enter a valid phone number (e.g., 79161234567 or +79161234567)')
            )
        ]
    )
    email = models.EmailField(
        max_length=254,
        blank=True,
        help_text=_('Email address'),
        db_index=True,
        verbose_name=_('Email')
    )
    archive = models.BooleanField(default=False, help_text=_('Is archived'), db_index=True)
    start_date = models.DateField(default=date.today, null=True, help_text=_('Work till'))
    end_date = models.DateField(null=True, blank=True, help_text=_('Fired date'))

    def clean(self):
        super().clean()
        if self.phone:
            self.phone = self.normalize_phone(self.phone)

    def normalize_phone(self, phone_number):
        """Normalize phone number to format 79161234567"""
        if not phone_number:
            return phone_number
        
        # Remove all characters except digits
        clean_phone = re.sub(r'[^\d]', '', phone_number)
        
        # If number starts with 8, replace with 7
        if clean_phone.startswith('8') and len(clean_phone) == 11:
            clean_phone = '7' + clean_phone[1:]
        
        # If number starts with 7 and has 11 digits - return as is
        if clean_phone.startswith('7') and len(clean_phone) == 11:
            return clean_phone
        
        # If number has 10 digits, add 7 at the beginning
        if len(clean_phone) == 10:
            return '7' + clean_phone
        
        # If nothing matched, return original number
        return phone_number

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = self.normalize_phone(self.phone)
        super().save(*args, **kwargs)
    
    @property
    def formatted_phone(self):
        """Return phone number in formatted display format"""
        if self.phone and len(self.phone) == 11 and self.phone.startswith('7'):
            return f"+{self.phone[0]} ({self.phone[1:4]}) {self.phone[4:7]}-{self.phone[7:9]}-{self.phone[9:11]}"
        return self.phone or ''

    class Meta:
        verbose_name = 'Employee'
        ordering = ['name']
