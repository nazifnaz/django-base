from django.contrib import admin
from django.contrib.admin import StackedInline

from order.models import Item, Cart


class ItemInline(StackedInline):
    model = Item
    extra = 0
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by',
                       'product', 'price', 'image_url',)

    fieldsets = (
        ('Product Name', {
            'fields': (('product', ),
                       )
        }),
        ('Product Information', {
            'fields': (('price',),
                       'image_url'
                       )
        }),

    )


class CartAdmin(admin.ModelAdmin):
    inlines = [ItemInline]
    list_display = ('id', 'customer', 'total', 'created_at',)
    fieldsets = (
        ('Cart information', {
            'fields': (('total',),
                       ('discount', 'cart_status'),
                       ('reference', 'notes'),
                       )
        }),
        ('Customer information', {
            'fields': (('customer',),)
        }),
        ('Invoice Information', {
            'fields': (('invoice_no', 'invoice_id'), ('order_date',))
        }),
        ('Payment Information', {
            'fields': (('transaction_id', 'payment_status'),
                       'failure_url', 'response_url')
        }),

        ('User Information', {
            'fields': (('created_at', 'updated_at', 'created_by', 'updated_by'),)
        }),

    )

    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by', 'total',
                       'customer', 'reference', 'discount', 'notes',  'response_url',
                       'failure_url', 'transaction_id', 'order_date', 'cart_status', 'payment_status', )


admin.site.register(Cart, CartAdmin)
