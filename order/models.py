from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from utils.code import generate_code


class Client(get_user_model()):
    """Service clients model.

    Relates with settings.AUTH_USER_MODEL with one-to-one relation. Contains
    additional `address` and `additional` fields, for more information check
    field `help_text` attribute.
    """

    address = models.TextField(_('address'), max_length=250)
    additional = models.TextField(
        _('additional info'),
        max_length=250,
        blank=True,
        help_text=_(
            'May to contain some personal and another important info.',
        ),
    )

    class Meta:
        verbose_name = _('client')
        verbose_name_plural = _('clients')


class AbstractOrderProperty(models.Model):
    """Abstract `Order` property model.

    Contains required `name` unique string field and `description`.
    """

    name = models.CharField(_('name'), max_length=25, unique=True)
    description = models.TextField(
        _('description'), max_length=250, blank=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name


class Color(AbstractOrderProperty):
    """`Order` color property."""

    class Meta:
        verbose_name = _('color')
        verbose_name_plural = _('colors')


class Size(AbstractOrderProperty):
    """`Order` size property."""

    class Meta:
        verbose_name = _('size')
        verbose_name_plural = _('sizes')


class Form(AbstractOrderProperty):
    """`Order` form property."""

    class Meta:
        verbose_name = _('form')
        verbose_name_plural = _('forms')


class OrderProperties(TimeStampedModel):
    """Abstract `Order` class.

    Contains foreign-key fields for `Color`, `Size` and `Form` models and
    `created` and `modified` datetime fields.
    """

    color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,
        verbose_name=_('color'),
    )
    size = models.ForeignKey(
        Size,
        on_delete=models.PROTECT,
        verbose_name=_('size'),
    )
    form = models.ForeignKey(
        Form,
        on_delete=models.PROTECT,
        verbose_name=_('form'),
    )

    class Meta:
        abstract = True


class StandardOrder(OrderProperties):
    """Standard set of order properties.

    If a client order has one of the standard sets of properties, then this
    order must enter the assembly instantly, otherwise expects the manager
    decision.
    """

    name = models.CharField(_('name'), max_length=25, unique=True)
    description = models.TextField(
        _('description'),
        max_length=250,
        blank=True,
    )

    class Meta:
        verbose_name = _('standard order properties')
        verbose_name_plural = _('standard orders properties')

    def __str__(self) -> str:
        return self.name


class Order(OrderProperties):
    """Client order is represented by this model."""

    class StatusChoice(models.TextChoices):
        """Order status choice.

        Attributes:
            RETURNED: the order is returned by the client
            CANCELLED: the order was cancelled by the manager or client
            IN_PROCESS: default field on order creation
            COMPLETED: the order was delivered to the client
        """

        RETURNED = 'returned'
        CANCELLED = 'cancelled'
        IN_PROCESS = 'in_process'
        COMPLETED = 'completed'

    class ProcessStatusChoice(models.TextChoices):
        """Order process status choice.

        If the order has a standard set of the properties (check the
        `StandardOrder` model) then default value should be `IN_ASSEMBLY`,
         otherwise - `PENDING`.

        Attributes:
            PENDING: the order expects the manager decision.
            IN_ASSEMBLY: the order is assembling by the picker.
            IN_DELIVERY: the order is delivering to the client.
            DELIVERED: the order completely delivered.
        """

        PENDING = 'pending', _('Expects the manager to accept it')
        IN_ASSEMBLY = 'in_assembly'
        IN_DELIVERY = 'in_delivery'
        DELIVERED = 'delivered'

    code = models.CharField(
        _('code'),
        max_length=40,
        default=generate_code,
        primary_key=True,
        editable=False,
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        verbose_name=_('client'),
        null=True,
    )

    status = models.CharField(
        _('status'),
        max_length=15,
        choices=StatusChoice.choices,
        default=StatusChoice.IN_PROCESS,
    )
    process = models.CharField(
        _('process status'),
        max_length=15,
        choices=ProcessStatusChoice.choices,
        default=ProcessStatusChoice.IN_ASSEMBLY,
    )

    comment = models.TextField(_('comment'), max_length=250, blank=True)

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        permissions = [
            (
                'manage_in_assembly_only',
                'Can manage an order with `in assembly` process status only',
            ),
            (
                'manage_in_delivery_only',
                'Can manage an order with `in delivery` process status only',
            ),
        ]


def validate_order_is_returned(order: Order):
    """Validate the order has `RETURNED` status.

    Raises:
        ValidationError: if the order status is not `RETURNED`.
    """
    if order.status != Order.StatusChoice.RETURNED:
        raise ValidationError(
            _(
                'Only a returned order can be related with `OrderReturn` '
                'model, but the given order [%(order)s] has a "%(status)s" '
                'status.',
            ),
            params={
                'order': order.code,
                'status': order.get_status_display(),
            },
        )


class OrderReturn(TimeStampedModel):
    """Client order return model."""

    class SolutionChoice(models.TextChoices):
        """Order return solution choice.

        Attributes:
            PENDING: the order return expects the manager decision
            MONEY: the manager decided to return money to the client
            NEW_ORDER: the manager decided to create new order for the client
        """

        PENDING = 'pending', _('pending')
        MONEY = 'money', _('return money to the client')
        NEW_ORDER = 'new_order', _(
            'create a new order to replace the returned one',
        )

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        verbose_name=_('order'),
        validators=[validate_order_is_returned]
    )

    solution = models.CharField(
        _('solution'),
        max_length=15,
        choices=SolutionChoice.choices,
        default=SolutionChoice.PENDING,
    )

    new_order = models.OneToOneField(
        Order,
        on_delete=models.SET_NULL,
        verbose_name=_('new order'),
        default=None,
        null=True,
        related_name='returned_for',
        help_text=_(
            'Set new `Order` instance if the solution is `new order`.',
        ),
    )

    class Meta:
        verbose_name = _('return order solution')
        verbose_name_plural = _('return order solutions')
