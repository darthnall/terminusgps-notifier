import decimal
from datetime import date

from django.test import TestCase, override_settings

from terminusgps_notifier import authorizenet


class GetSubscriptionContractTestCase(TestCase):
    def test_required_attributes_present_in_contract(self):
        """Fails if :py:func:`get_subscription_contract` returns an invalid contract."""
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
        generated_contract = authorizenet.get_subscription_contract(**kwargs)
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
        """Succeeds if :py:func:`get_subscription_contract` returns a subscription contract without providing ``start_date``."""
        kwargs = {
            "profile_id": "1",
            "address_id": "2",
            "payment_id": "3",
            "start_date": None,
        }
        generated_contract = authorizenet.get_subscription_contract(**kwargs)
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
