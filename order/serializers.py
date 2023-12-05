from rest_framework import serializers

from order.models import Client, Order, OrderReturn


class LoginSerializer(serializers.Serializer):
    """Login serializers model.

    Contains required `username` and `password` fields.
    """

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128)


class ClientPersonalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = (
            'id', 'username', 'email',
            'first_name', 'last_name', 'address',
        )


class OrderSerializer(serializers.ModelSerializer):
    """`Order` model serializer."""

    class Meta:
        model = Order
        fields = (
            'code', 'client',
            'color', 'size', 'form',
            'status', 'process',
            'created', 'modified',
        )


class OrderReturnSerializer(serializers.ModelSerializer):
    """`OrderReturn` model serializer."""

    class Meta:
        model = OrderReturn
        fields = ('id', 'order', 'solution', 'new_order')


class OrderPropertySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=25)
    description = serializers.CharField(max_length=250, default='')
