from django.contrib import admin

from bdo.main import models


class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'f_time',
        'service_prov_id',
        'invoke_id',
        'content_tag',
        'command_tag'
    )
    list_display_links = (
        'f_time',
        'service_prov_id',
        'invoke_id',
        'content_tag',
        'command_tag'
    )
    list_filter = [
        'content_tag',
        'service_prov_id'
    ]
    list_per_page = 20
    search_fields = [
        'invoke_id',
        'command_tag',
        'original',
    ]

    def f_time(self, obj):
        return obj.message_date_time.strftime("%x %X")
    f_time.short_description = 'timestamp'


class SubscriptionVersionAdmin(admin.ModelAdmin):
    list_display = (
        'active',
        'subscription_version_tn',
        'subscription_download_reason',
        'subscription_rn1',
    )
    list_display_links = (
        'subscription_version_tn',
    )
    list_filter = [
        'active',
        'subscription_rn1',
        'subscription_download_reason',
        'subscription_line_type',
    ]
    list_per_page = 20
    search_fields = [
        'subscription_version_id',
        'subscription_version_tn',
    ]


admin.site.register(models.Message, MessageAdmin)
admin.site.register(models.SubscriptionVersion, SubscriptionVersionAdmin)
