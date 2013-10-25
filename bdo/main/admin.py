from django.contrib import admin

from bdo.main import models


class BDOMessageAdmin(admin.ModelAdmin):
    list_filter = [
        'outbound',
    ]
    search_fields = [
        'description',
        'message',
    ]


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


admin.site.register(models.BDOMessage, BDOMessageAdmin)
admin.site.register(models.SubscriptionVersion, SubscriptionVersionAdmin)
