from django.contrib import admin

from bdosoa.main import models


class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'f_time',
        'service_prov_id',
        'invoke_id',
        'command_tag',
    )
    list_display_links = (
        'f_time',
        'service_prov_id',
        'invoke_id',
        'command_tag',
    )
    list_filter = [
        'command_tag',
        'service_prov_id',
    ]
    list_per_page = 20
    search_fields = [
        'invoke_id',
        'command_tag',
        'xml',
    ]

    def f_time(self, obj):
        return obj.message_date_time.strftime("%x %X")
    f_time.short_description = 'timestamp'


class SubscriptionVersionAdmin(admin.ModelAdmin):
    list_display = (
        'subscription_version_tn',
        'subscription_line_type',
        'subscription_download_reason',
        'subscription_rn1',
        'subscription_lnp_type',
    )
    list_display_links = (
        'subscription_version_tn',
    )
    list_filter = [
        'subscription_download_reason',
        'subscription_line_type',
        'subscription_rn1',
    ]
    list_per_page = 20
    search_fields = [
        'subscription_version_id',
        'subscription_version_tn',
    ]


admin.site.register(models.Message, MessageAdmin)
admin.site.register(models.SubscriptionVersion, SubscriptionVersionAdmin)
