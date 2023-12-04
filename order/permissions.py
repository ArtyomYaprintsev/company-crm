from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.utils.translation import gettext_lazy as _

from order.models import Order


class ClientOnlyPermission(BasePermission):
    message = _('The action is allowed only for service clients.')

    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'client'))


class UpdateDeliveredOrderOnly(BasePermission):
    message = _('The action is allowed only for delivered orders.')

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return (
            obj.process == Order.ProcessStatusChoice.DELIVERED
            and obj.status in (
                Order.StatusChoice.IN_PROCESS,
                Order.StatusChoice.COMPLETED,
            )
        )
