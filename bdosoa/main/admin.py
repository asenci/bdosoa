from django.contrib import admin

from bdosoa.main import models


class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'f_time',
        'direction',
        'service_prov_id',
        'invoke_id',
        'command_tag',
        'status',
    )
    list_display_links = (
        'f_time',
        'direction',
        'service_prov_id',
        'invoke_id',
        'command_tag',
        'status',
    )
    list_filter = [
        'service_prov_id',
        'direction',
        'status',
        'command_tag',
    ]
    list_per_page = 20
    search_fields = [
        'invoke_id',
        'command_tag',
        'xml',
        'error',
    ]

    # noinspection PyMethodMayBeStatic
    def f_time(self, obj):
        return obj.message_date_time.strftime("%x %X")
    f_time.short_description = 'timestamp'


class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = (
        'service_prov_id',
        'spg_soap_url',
        'enabled',
    )
    list_display_links = (
        'service_prov_id',
        'spg_soap_url',
    )
    list_filter = [
        'enabled',
    ]
    search_fields = [
        'service_prov_id',
        'spg_soap_url',
    ]


class SubscriptionVersionAdmin(admin.ModelAdmin):
    list_display = (
        'service_prov_id',
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
        'service_prov_id',
        'subscription_download_reason',
        'subscription_line_type',
        'subscription_rn1',
    ]
    list_per_page = 20
    search_fields = [
        'subscription_version_id',
        'subscription_version_tn',
    ]


admin.site.register(models.ServiceProvider, ServiceProviderAdmin)
admin.site.register(models.Message, MessageAdmin)
admin.site.register(models.SubscriptionVersion, SubscriptionVersionAdmin)
