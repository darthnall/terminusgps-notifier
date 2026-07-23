from unittest.mock import patch

from django.test import TestCase
from terminusgps.authorizenet.service import AuthorizenetError

from terminusgps_notifier.constants import SUBSCRIPTION_NOT_FOUND
from terminusgps_notifier.models import Profile


class ProfileTestCase(TestCase):
    fixtures = [
        "terminusgps_notifier/tests/test_user.json",
        "terminusgps_notifier/tests/test_profile.json",
    ]

    def test_get_destination_phone_numbers_with_saved_phones(self) -> None:
        """Fails if :py:meth:`get_destination_phone_numbers` doesn't return a list of phone numbers."""
        test_unit_id = 12345678
        expected_phones = ["+17135555555", "+18325555555"]
        with patch(
            "terminusgps_notifier.models.get_phones",
            return_value=expected_phones,
        ):
            test_profile = Profile.objects.get(pk=1)
            result = test_profile.get_destination_phone_numbers(test_unit_id)
            self.assertEqual(result, expected_phones)

    def test_get_destination_phone_numbers_without_saved_phones(self) -> None:
        """Fails if :py:meth:`get_destination_phone_numbers` returns a list of phone numbers for a unit without any."""
        test_unit_id = 12345678
        expected_phones = []
        with patch("terminusgps_notifier.models.get_phones", return_value=[]):
            test_profile = Profile.objects.get(pk=1)
            result = test_profile.get_destination_phone_numbers(test_unit_id)
            self.assertEqual(result, expected_phones)

    def test_has_available_messages_with_available_messages(self):
        """Fails if :py:meth:`has_available_messages` returns :py:obj:`False` with available messages."""
        test_profile = Profile.objects.get(pk=1)
        test_profile.messages_count = 0
        test_profile.messages_limit = 500
        test_profile.save(update_fields=["messages_count", "messages_limit"])
        self.assertTrue(test_profile.has_available_messages())
        test_profile.messages_count = 499
        test_profile.messages_limit = 500
        test_profile.save(update_fields=["messages_count", "messages_limit"])
        self.assertTrue(test_profile.has_available_messages())

    def test_has_available_messages_with_max_messages(self):
        """Fails if :py:meth:`has_available_messages` returns :py:obj:`True` with maxed messages."""
        test_profile = Profile.objects.get(pk=1)
        test_profile.messages_count = 500
        test_profile.messages_count = 500
        test_profile.save(update_fields=["messages_count", "messages_limit"])
        self.assertFalse(test_profile.has_available_messages())
        test_profile.messages_count = 501
        test_profile.messages_limit = 500
        test_profile.save(update_fields=["messages_count", "messages_limit"])
        self.assertFalse(test_profile.has_available_messages())

    def test_update_messages_count_and_save(self):
        """Fails if :py:meth:`update_messages_count_and_save` doesn't increment :py:attr:`messages_count` and save."""
        test_profile = Profile.objects.get(pk=1)
        test_profile.messages_count = 0
        test_profile.messages_limit = 500
        test_profile.save(update_fields=["messages_count", "messages_limit"])
        test_profile.update_messages_count_and_save(num_messages=1)
        self.assertEqual(test_profile.messages_count, 1)

    def test_has_active_subscription_with_no_subscription_id(self):
        """Fails if :py:meth:`has_active_subscription` returns :py:obj:`True` with no :py:attr:`subscription_id` set on the profile."""
        test_profile = Profile.objects.get(pk=1)
        test_profile.subscription_id = ""
        test_profile.save(update_fields=["subscription_id"])
        self.assertFalse(test_profile.has_active_subscription())

    def test_has_active_subscription_with_active_status(self):
        """Fails if :py:meth:`has_active_subscription` doesn't return :py:obj:`True` with a status of 'active'."""
        with patch(
            "terminusgps_notifier.models.get_subscription_status",
            return_value="active",
        ):
            test_profile = Profile.objects.get(pk=1)
            self.assertTrue(test_profile.has_active_subscription())

    def test_has_active_subscription_with_canceled_status(self):
        """Fails if :py:meth:`has_active_subscription` doesn't return :py:obj:`True` with a status of 'canceled'."""
        with patch(
            "terminusgps_notifier.models.get_subscription_status",
            return_value="canceled",
        ):
            test_profile = Profile.objects.get(pk=1)
            self.assertTrue(test_profile.has_active_subscription())

    def test_has_active_subscription_with_suspended_status(self):
        """Fails if :py:meth:`has_active_subscription` doesn't return :py:obj:`False` with a status of 'canceled'."""
        with patch(
            "terminusgps_notifier.models.get_subscription_status",
            return_value="suspended",
        ):
            test_profile = Profile.objects.get(pk=1)
            self.assertFalse(test_profile.has_active_subscription())

    def test_has_active_subscription_with_terminated_status(self):
        """Fails if :py:meth:`has_active_subscription` doesn't return :py:obj:`False` with a status of 'canceled'."""
        with patch(
            "terminusgps_notifier.models.get_subscription_status",
            return_value="terminated",
        ):
            test_profile = Profile.objects.get(pk=1)
            self.assertFalse(test_profile.has_active_subscription())

    def test_has_active_subscription_with_expired_status(self):
        """Fails if :py:meth:`has_active_subscription` doesn't return :py:obj:`False` with a status of 'canceled'."""
        with patch(
            "terminusgps_notifier.models.get_subscription_status",
            return_value="expired",
        ):
            test_profile = Profile.objects.get(pk=1)
            self.assertFalse(test_profile.has_active_subscription())

    def test_has_active_subscription_subscription_not_found(self):
        """Fails if the subscription wasn't found in Authorizenet and :py:meth:`has_active_subscription` doesn't return :py:obj:`False`."""
        with patch(
            "terminusgps_notifier.models.get_subscription_status",
            side_effect=AuthorizenetError(
                message="Subscription not found", code=SUBSCRIPTION_NOT_FOUND
            ),
        ):
            test_profile = Profile.objects.get(pk=1)
            self.assertFalse(test_profile.has_active_subscription())

    def test_has_active_subscription_authorizeneterror_reraised(self):
        """Fails if :py:exec:`AuthorizenetError` was raised by the method and not re-raised."""
        with patch(
            "terminusgps_notifier.models.get_subscription_status",
            side_effect=AuthorizenetError(
                message="Unknown Error", code="E00001"
            ),
        ):
            test_profile = Profile.objects.get(pk=1)
            with self.assertRaises(AuthorizenetError):
                test_profile.has_active_subscription()
