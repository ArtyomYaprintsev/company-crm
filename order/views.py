from typing import Union

from django.contrib.auth import authenticate
from django.http import QueryDict
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from rest_framework import mixins, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from order import models, serializers
from order.permissions import ClientOnlyPermission, UpdateDeliveredOrderOnly


def service(request):
    return render(request, 'index.html')


class LoginUser(APIView):
    """Login user view.

    Returns the authentication token on success login.
    """

    serializer_class = serializers.LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, **kwargs):
        """Authenticate user and return related token."""
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(
            username=serializer.data.get('username'),
            password=serializer.data.get('password'),
        )

        if not user:
            return Response({
                'details': _('Unable to login with provided credentials.'),
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                'details': _('User account not active.'),
            }, status=status.HTTP_401_UNAUTHORIZED)

        token, is_created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)


class ClientPersonalView(APIView):
    serializer_class = serializers.ClientPersonalSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        ClientOnlyPermission,
    )

    def get(self, request, **kwargs):
        return Response(self.serializer_class(request.user.client).data)


class OrderPropertiesView(APIView):
    serializers_class = serializers.OrderPropertySerializer
    permission_classes = (permissions.AllowAny,)

    def get(self, request, **kwargs):
        return Response({
            model._meta.model_name: self.serializers_class(
                model.objects.all(),
                many=True,
            ).data
            for model in [models.Color, models.Size, models.Form]
        })


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """Viewset for the client to manage orders.

    Allows `list`, `create` and `retrieve` actions.
    """

    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        ClientOnlyPermission,
        UpdateDeliveredOrderOnly,
    )

    def get_queryset(self) -> Union[QuerySet, list[models.Order]]:
        """Get authenticated user orders.

        Returns empty orders list if the request is missing, otherwise - user
        related orders.
        """
        if not self.request:
            return models.Order.objects.none()

        return super().get_queryset().filter(client=self.request.user)

    def create(self, request, *args, **kwargs):
        """Extends default `create` behavior.

        Sets the `client` field as requested user id and the `process` field
        if the order has the standard set of properties.
        """
        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        # Set process to pending if the order is not standard
        if not models.StandardOrder.objects.filter(
            **{
                prop: request.data.get(prop)
                for prop in ['color', 'size', 'form']
            },
        ).exists():
            request.data['process'] = models.Order.ProcessStatusChoice.PENDING

        request.data['client'] = request.user.pk

        return super().create(request, *args, **kwargs)

    @action(
        methods=['POST'], detail=True,
        url_path='return', url_name='return',
    )
    def return_order(self, request, **kwargs):
        """Apply a request to return the order."""
        # pylint: disable=unused-argument
        order: models.Order = self.get_object()

        # Change order status to returned
        order.status = models.Order.StatusChoice.RETURNED
        order.save()

        # Create related `OrderReturn` instance
        serializer = serializers.OrderReturnSerializer(
            data={'order': order.pk},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data),
        )
