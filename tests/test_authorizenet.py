import decimal
from datetime import date
from unittest.mock import patch

from django.test import TestCase, override_settings
from terminusgps.authorizenet.service import AuthorizenetError

from terminusgps_notifier import authorizenet


class BuildSubscriptionContractTestCase(TestCase):
    def test_required_attributes_present_in_contract(self):
        """Fails if :py:func:`build_subscription_contract` returns an invalid contract."""
        kwargs = {
            "profile_id": "1",
            "address_id": "2",
            "payment_id": "3",
            "start_date": date.today(),
            "amount": decimal.Decimal("60.00"),
            "trial_amount": decimal.Decimal("0.00"),
            "total_occurrences": 9999,
            "trial_occurrences": 0,
            "interval_length": 1,
            "interval_unit": "months",
        }
        generated_contract = authorizenet.build_subscription_contract(**kwargs)
        self.assertEqual(
            generated_contract.profile.customerProfileId, kwargs["profile_id"]
        )
        self.assertEqual(
            generated_contract.profile.customerAddressId, kwargs["address_id"]
        )
        self.assertEqual(
            generated_contract.profile.customerPaymentProfileId,
            kwargs["payment_id"],
        )
        self.assertEqual(
            generated_contract.paymentSchedule.startDate.day,
            kwargs["start_date"].day,
        )
        self.assertEqual(
            generated_contract.paymentSchedule.startDate.month,
            kwargs["start_date"].month,
        )
        self.assertEqual(
            generated_contract.paymentSchedule.startDate.year,
            kwargs["start_date"].year,
        )
        self.assertEqual(generated_contract.amount, kwargs["amount"])
        self.assertEqual(
            generated_contract.trialAmount, kwargs["trial_amount"]
        )
        self.assertEqual(
            generated_contract.paymentSchedule.totalOccurrences,
            kwargs["total_occurrences"],
        )
        self.assertEqual(
            generated_contract.paymentSchedule.trialOccurrences,
            kwargs["trial_occurrences"],
        )
        self.assertEqual(
            generated_contract.paymentSchedule.interval.length,
            kwargs["interval_length"],
        )
        self.assertEqual(
            generated_contract.paymentSchedule.interval.unit,
            kwargs["interval_unit"],
        )

    def test_start_date_not_provided(self):
        """Succeeds if :py:func:`build_subscription_contract` returns a subscription contract without providing ``start_date``."""
        kwargs = {
            "profile_id": "1",
            "address_id": "2",
            "payment_id": "3",
            "start_date": None,
        }
        generated_contract = authorizenet.build_subscription_contract(**kwargs)
        self.assertTrue(
            hasattr(generated_contract.paymentSchedule, "startDate")
        )
        self.assertIsInstance(
            generated_contract.paymentSchedule.startDate, date
        )


class GetHostedProfilePageUrlTestCase(TestCase):
    @override_settings(DEBUG=True)
    def test_debug_true(self):
        """Fails if the wrong url was returned with debug mode on."""
        url = authorizenet.get_hosted_profile_page_url()
        self.assertEqual(url, "https://test.authorize.net/customer/manage")

    @override_settings(DEBUG=False)
    def test_debug_false(self):
        """Fails if the wrong url was returned with debug mode off."""
        url = authorizenet.get_hosted_profile_page_url()
        self.assertEqual(url, "https://accept.authorize.net/customer/manage")


class SubscriptionIsActiveTestCase(TestCase):
    def test_no_id_provided_returns_false(self):
        """Fails if :py:obj:`False` wasn't returned with no id provided."""
        result = authorizenet.subscription_is_active(id=None)
        self.assertFalse(result)

    def test_active_subscription_returns_true(self):
        """Fails if :py:obj:`True` wasn't returned with an active subscription."""
        with patch(
            "terminusgps_notifier.authorizenet.get_subscription_status",
            return_value="active",
        ):
            result = authorizenet.subscription_is_active(id=1)
            self.assertTrue(result)

    def test_canceled_subscription_returns_true(self):
        """Fails if :py:obj:`True` wasn't returned with a canceled subscription."""
        with patch(
            "terminusgps_notifier.authorizenet.get_subscription_status",
            return_value="canceled",
        ):
            result = authorizenet.subscription_is_active(id=1)
            self.assertTrue(result)

    def test_terminated_subscription_returns_false(self):
        """Fails if :py:obj:`False` wasn't returned with a terminated subscription."""
        with patch(
            "terminusgps_notifier.authorizenet.get_subscription_status",
            return_value="terminated",
        ):
            result = authorizenet.subscription_is_active(id=1)
            self.assertFalse(result)

    def test_suspended_subscription_returns_false(self):
        """Fails if :py:obj:`False` wasn't returned with a suspended subscription."""
        with patch(
            "terminusgps_notifier.authorizenet.get_subscription_status",
            return_value="suspended",
        ):
            result = authorizenet.subscription_is_active(id=1)
            self.assertFalse(result)

    def test_expired_subscription_returns_false(self):
        """Fails if :py:obj:`False` wasn't returned with a expired subscription."""
        with patch(
            "terminusgps_notifier.authorizenet.get_subscription_status",
            return_value="expired",
        ):
            result = authorizenet.subscription_is_active(id=1)
            self.assertFalse(result)

    def test_authorizeneterror_reraised(self):
        """Fails if an Authorizenet error was raised but not reraised."""
        with patch(
            "terminusgps_notifier.authorizenet.get_subscription_status",
            side_effect=AuthorizenetError(message="", code="E00000"),
        ):
            with self.assertRaises(AuthorizenetError):
                authorizenet.subscription_is_active(id=1)

    def test_authorizeneterror_e00035_returns_false(self):
        """Fails if an Authorizenet error E00035 was raised and the return value was not :py:obj:`False`."""
        with patch(
            "terminusgps_notifier.authorizenet.get_subscription_status",
            side_effect=AuthorizenetError(message="", code="E00035"),
        ):
            result = authorizenet.subscription_is_active(id=1)
            self.assertFalse(result)
