from django.contrib import admin
from .models import Coupon, Item, OrderItem, Order, Refund, Address


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered', 'being_delivered', 'billing_address',
                    'recieved', 'refund_granted', 'refund_requested', 'user', 'payment', 'coupon']
    list_filter = ['user', 'ordered', 'being_delivered',
                   'recieved', 'refund_granted', 'refund_requested']
    list_display_links = ['user', 'billing_address',
                          'payment', 'coupon']
    search_fields = ['user__username', 'ref_code']
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'Zip',
        'default',
    ]

    list_filter = [
        'country',
        'default',
    ]
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']

# Register your models here.


admin.site.register(OrderItem)
admin.site.register(Item)
admin.site.register(Order, OrderAdmin)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
