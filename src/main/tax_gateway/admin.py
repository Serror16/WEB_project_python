from django.contrib import admin
from .models import Tax, AuditLog

admin.site.register(Tax)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'method', 'path', 'status_code', 'processing_time_ms', 'user')
    list_filter = ('method', 'status_code', 'timestamp')
    search_fields = ('path', 'request_payload', 'response_payload')
    readonly_fields = ('timestamp', 'path', 'method', 'user', 'status_code', 'processing_time_ms', 'request_payload', 'response_payload')