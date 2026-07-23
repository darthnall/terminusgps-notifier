from authorizenet import apicontractsv1, apicontrollers
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from encrypted_field import EncryptedField
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet.service import AuthorizenetError

from terminusgps_notifier.authorizenet import get_merchant_auth
from terminusgps_notifier.constants import SUBSCRIPTION_NOT_FOUND
from terminusgps_notifier.wialon import get_phones


class Profile(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="notifier_profile",
    )
    messages_count = models.PositiveIntegerField(default=0)
    messages_limit = models.PositiveIntegerField(default=500)
    token = EncryptedField(blank=True, null=True, default=None)
    profile_id = models.CharField(blank=True, max_length=50)
    description = models.CharField(blank=True, max_length=50)
    merchant_id = models.CharField(blank=True, max_length=50)
    subscription_id = models.CharField(blank=True, max_length=50)

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")

    def __str__(self) -> str:
        return str(self.user)

    def create_authorizenet_customer_profile_and_save(
        self,
        email: str | None = None,
        merchant_id: str | None = None,
        description: str | None = None,
        reference_id: str | None = None,
    ) -> None:
        """
        Creates a customer profile in Authorizenet then saves its data to the profile.

        :param email: Optional. An email address.
        :type email: str | None
        :param merchant_id: Optional. A merchant-designated id.
        :type merchant_id: str | None
        :param description: Optional. Customer profile description.
        :type description: str | None
        :param reference_id: Optional. Authorizenet API call reference id.
        :type reference_id: str | None
        :returns: Nothing.
        :rtype: None

        """
        first_name = self.user.first_name
        last_name = self.user.last_name
        full_name = f"{first_name} {last_name}"
        email = email or self.user.email
        merchant_id = merchant_id or full_name
        description = description or f"{full_name}'s profile"
        profile = apicontractsv1.customerProfileType()
        profile.email = email
        profile.merchantCustomerId = merchant_id
        profile.description = description
        request = apicontractsv1.createCustomerProfileRequest()
        request.merchantAuthentication = get_merchant_auth()
        request.profile = profile
        if reference_id is not None:
            request.refId = reference_id
        controller = apicontrollers.createCustomerProfileController(request)
        controller.execute()
        response = controller.getresponse()
        if (
            not hasattr(response, "messages")
            or response.messages.resultCode != "Ok"
        ):
            raise AuthorizenetError(
                response.messages.message[0]["text"].text,
                response.messages.message[0]["code"].text,
            )
        self.profile_id = str(response.customerProfileId)
        self.merchant_id = merchant_id
        self.description = description
        self.save(update_fields=["profile_id", "merchant_id", "description"])

    def cancel_authorizenet_subscription(
        self, reference_id: str | None = None
    ) -> ObjectifiedElement:
        request = apicontractsv1.ARBCancelSubscriptionRequest()
        request.merchantAuthentication = get_merchant_auth()
        request.subscriptionId = self.subscription_id
        if reference_id is not None:
            request.refId = reference_id
        controller = apicontrollers.ARBCancelSubscriptionController(request)
        controller.execute()
        response = controller.getresponse()
        if not all(
            [
                hasattr(response, "messages"),
                response.messages.resultCode == "Ok",
            ]
        ):
            raise AuthorizenetError(
                response.messages.message[0]["text"].text,
                response.messages.message[0]["code"].text,
            )
        return response

    def get_authorizenet_subscription_status(
        self, reference_id: str | None = None
    ) -> str | None:
        request = apicontractsv1.ARBGetSubscriptionStatusRequest()
        request.merchantAuthentication = get_merchant_auth()
        request.subscriptionId = self.subscription_id
        if reference_id is not None:
            request.refId = reference_id
        controller = apicontrollers.ARBGetSubscriptionStatusController(request)
        controller.execute()
        response = controller.getresponse()
        if not all(
            [
                hasattr(response, "messages"),
                hasattr(response, "status"),
                response.messages.resultCode == "Ok",
            ]
        ):
            raise AuthorizenetError(
                response.messages.message[0]["text"].text,
                response.messages.message[0]["code"].text,
            )
        return getattr(response, "status", None)

    def get_wialon_destination_phone_numbers(self, unit_id: int) -> list[str]:
        """Returns destination phone numbers for a Wialon unit by id."""
        return get_phones(self.token, unit_id)

    def set_wialon_api_token_and_save(self, token: str) -> None:
        """Sets :py:attr:`token` to ``token`` then saves."""
        self.token = str(token)
        self.save(update_fields=["token"])

    def update_messages_count_and_save(self, num_messages: int) -> None:
        """Increments :py:attr:`messages_count` by ``num_messages`` then saves."""
        self.messages_count = models.F("messages_count") + num_messages
        self.save(update_fields=["messages_count"])

    def has_available_messages(self) -> bool:
        """Returns whether the profile has reached its messaging limit."""
        return self.messages_count < self.messages_limit

    def has_active_subscription(self) -> bool:
        """Returns whether the profile has an active subscription."""
        if not self.subscription_id:
            return False
        try:
            status = self.get_authorizenet_subscription_status()
        except AuthorizenetError as error:
            if error.code == SUBSCRIPTION_NOT_FOUND:
                return False
            raise
        else:
            return status in ("active", "canceled")


class DispatchLog(models.Model):
    user_id = models.IntegerField()
    unit_id = models.IntegerField()
    message = models.CharField(max_length=1024)
    msg_time_int = models.IntegerField()
    phones = models.JSONField(default=list)
    method = models.CharField(
        choices=[("sms", _("SMS")), ("voice", _("Voice"))]
    )
    pub_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("dispatch log")
        verbose_name_plural = _("dispatch logs")

    def __str__(self) -> str:
        return f"DispatchLog #{self.pk}"
