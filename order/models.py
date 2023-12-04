from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django_extensions.db.models import TimeStampedModel

from utils.code import generate_code


class Client(get_user_model()):
    address = models.TextField(_('address'), max_length=250)
    additional = models.TextField(
        _('additional info'),
        max_length=250,
        blank=True,
        help_text=_(
            'May to contains some personal and another important info',
        ),
    )

    class Meta:
        verbose_name = _('client')
        verbose_name_plural = _('clients')


class AbstractOrderProperty(models.Model):
    name = models.CharField(_('name'), max_length=25, unique=True)
    description = models.TextField(
        _('description'), max_length=250, blank=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name


class Color(AbstractOrderProperty):
    class Meta:
        verbose_name = _('color')
        verbose_name_plural = _('colors')


class Size(AbstractOrderProperty):
    class Meta:
        verbose_name = _('size')
        verbose_name_plural = _('sizes')


class Form(AbstractOrderProperty):
    class Meta:
        verbose_name = _('form')
        verbose_name_plural = _('forms')


class OrderProperties(TimeStampedModel):
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
    class StatusChoice(models.TextChoices):
        RETURNED = 'returned'
        CANCELLED = 'cancelled'
        IN_PROCESS = 'in_process'
        COMPLETED = 'completed'

    class ProcessStatusChoice(models.TextChoices):
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


def validate_order_is_returned(value: Order):
    if value.status != Order.StatusChoice.RETURNED:
        raise ValidationError(
            _(
                'Only a returned order can be related with `OrderReturn` '
                'model, but the given order [%(order)s] has a "%(status)s" '
                'status.',
            ),
            params={
                'order': value.code,
                'status': value.get_status_display(),
            },
        )


class OrderReturn(TimeStampedModel):
    class SolutionChoice(models.TextChoices):
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
