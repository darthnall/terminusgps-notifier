from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from encrypted_field import EncryptedField
from terminusgps.authorizenet.service import AuthorizenetError

from terminusgps_notifier.authorizenet import get_subscription_status
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

    def get_destination_phone_numbers(self, unit_id: int) -> list[str]:
        return get_phones(self.token, unit_id)

    def update_messages_count_and_save(self, num_messages: int) -> None:
        self.messages_count = models.F("messages_count") + num_messages
        self.save(update_fields=["messages_count"])

    def has_available_messages(self) -> bool:
        return self.messages_count < self.messages_limit

    def has_active_subscription(self) -> bool:
        if not self.subscription_id:
            return False
        try:
            status = get_subscription_status(int(self.subscription_id))
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
