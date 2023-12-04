from rest_framework import serializers

from order.models import Order, OrderReturn


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            'code', 'client',
            'color', 'size', 'form',
            'status', 'process',
            'created', 'modified',
        )


class OrderReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderReturn
        fields = ('id', 'order', 'solution', 'new_order')
