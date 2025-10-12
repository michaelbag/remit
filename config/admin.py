from django.contrib import admin
from django.utils.html import format_html
from .models import ExtSystem


@admin.register(ExtSystem)
class ExtSystemAdmin(admin.ModelAdmin):
    list_display = ('title', 'guid', 'enabled', 'created_datetime', 'last_ping_datetime')
    list_filter = ('enabled', 'created_datetime', 'last_ping_datetime')
    search_fields = ('title', 'guid')
    readonly_fields = ('guid', 'created_datetime', 'copy_guid_button')
    ordering = ('-created_datetime',)
    change_form_template = 'admin/config/extsystem/change_form.html'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'enabled')
        }),
        ('System Information', {
            'fields': ('guid', 'copy_guid_button', 'created_datetime', 'last_ping_datetime'),
            'classes': ('collapse',)
        }),
    )
    
    def copy_guid_button(self, obj):
        """Display a copy button for the GUID field"""
        if obj.pk:
            return format_html(
                '''
                <div style="margin-top: 10px;">
                    <input type="button" class="default" value="📋 Copy GUID to Clipboard" onclick="copyGuidToClipboard('{}')" />
                </div>
                ''',
                str(obj.guid)
            )
        return "-"
    copy_guid_button.short_description = "Copy GUID"
    copy_guid_button.allow_tags = True
