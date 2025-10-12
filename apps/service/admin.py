from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Operation


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'archive', 'qr_codes_count', 'created', 'modified')
    list_filter = ('archive', 'created', 'modified')
    search_fields = ('code', 'name', 'description', 'comment')
    ordering = ('name', 'code')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('code', 'name', 'description')
        }),
        (_('Status'), {
            'fields': ('archive',)
        }),
        (_('Associated QR Codes'), {
            'fields': ('qr_codes_list',),
            'description': _('QR codes associated with this operation')
        }),
        (_('Additional Information'), {
            'fields': ('comment',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created', 'modified', 'qr_codes_list')
    
    def qr_codes_count(self, obj):
        """Display count of associated QR codes"""
        return obj.qr_codes_operations.count()
    qr_codes_count.short_description = _('QR Codes Count')
    qr_codes_count.admin_order_field = 'qr_codes_operations__count'
    
    def qr_codes_list(self, obj):
        """Display list of associated QR codes with links"""
        qr_codes = obj.qr_codes_operations.all()
        if not qr_codes:
            return "-"
        
        links = []
        for qr_code in qr_codes:
            url = f"/admin/qr/qrcode/{qr_code.guid}/change/"
            # Display title with short_public_code in brackets, or just short_public_code if title is empty
            if qr_code.title:
                display_text = f"{qr_code.title} ({qr_code.short_public_code})"
            else:
                display_text = qr_code.short_public_code
            links.append(f'<a href="{url}" target="_blank">{display_text}</a>')
        
        return format_html('<br>'.join(links))
    qr_codes_list.short_description = _('Associated QR Codes')
    qr_codes_list.allow_tags = True
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('qr_codes_operations')