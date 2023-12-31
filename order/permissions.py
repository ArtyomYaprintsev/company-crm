from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import SAFE_METHODS, BasePermission

from order.models import Order


class ClientOnlyPermission(BasePermission):
    """Allows access for service clients.

    Checks that user have related `order.Client` model.
    """

    message = _('The action is allowed only for service clients.')

    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'client'))


class UpdateDeliveredOrderOnly(BasePermission):
    """Allows access for delivered orders only."""

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
