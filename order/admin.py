from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _

from order import models


@admin.register(models.Client)
class ClientAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"), {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "address",
                    "additional",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('username', 'email')
    list_filter = ()


class OrderPropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(models.Color)
class ColorAdmin(OrderPropertyAdmin):
    pass


@admin.register(models.Size)
class SizeAdmin(OrderPropertyAdmin):
    pass


@admin.register(models.Form)
class FormAdmin(OrderPropertyAdmin):
    pass


@admin.register(models.StandardOrder)
class StandardOrderAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'size',
        'form',
    )
    search_fields = ('name',)


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'client',
        'status',
        'process',
        'created',
        'modified',
    )
    list_filter = ('created', 'status', 'process')
    actions = (
        'update_order_to_in_assembly_status',
        'update_order_to_in_delivery_status',
        'complete_order',
    )

    def has_in_assembly_only_permission(self, request):
        return request.user.has_perm(
            "%s.%s" % (self.opts.app_label, 'manage_in_assembly_only'),
        )

    def has_in_delivery_only_permission(self, request):
        return request.user.has_perm(
            "%s.%s" % (self.opts.app_label, 'manage_in_delivery_only'),
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        queryset = super().get_queryset(request)

        if request.user:
            if request.user.is_superuser:
                return queryset

            if self.has_in_assembly_only_permission(request):
                return queryset.filter(
                    process=models.Order.ProcessStatusChoice.IN_ASSEMBLY,
                )

            if self.has_in_delivery_only_permission(request):
                return queryset.filter(
                    process=models.Order.ProcessStatusChoice.IN_DELIVERY,
                )

            return queryset

        return self.model._default_manager.none()

    @admin.action(
        permissions=('change',),
        description='Set selected orders process status to `in assembly`',
    )
    def update_order_to_in_assembly_status(self, request, queryset):
        return queryset.update(
            process=models.Order.ProcessStatusChoice.IN_ASSEMBLY,
        )

    @admin.action(
        permissions=('in_assembly_only',),
        description='Set selected orders process status to `in delivery`',
    )
    def update_order_to_in_delivery_status(self, request, queryset):
        return queryset.update(
            process=models.Order.ProcessStatusChoice.IN_DELIVERY,
        )

    @admin.action(
        permissions=('in_delivery_only',),
        description='Set selected orders as process status to `delivered`',
    )
    def complete_order(self, request, queryset):
        return queryset.update(
            status=models.Order.StatusChoice.COMPLETED,
            process=models.Order.ProcessStatusChoice.DELIVERED,
        )


@admin.register(models.OrderReturn)
class OrderReturnAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'solution',
        'new_order',
        'modified',
    )
    list_filter = ('created', 'modified', 'solution')
