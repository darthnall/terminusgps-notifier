from django.test import TestCase

from terminusgps_notifier.forms import (
    AddressTriggerForm,
    GeofenceTriggerForm,
    SpeedTriggerForm,
    WialonSensorType,
)


class GeofenceTriggerFormTestCase(TestCase):
    def setUp(self) -> None:
        self.form_cls = GeofenceTriggerForm
        self.valid_test_data = {
            "sensor_type": WialonSensorType.ANY,
            "sensor_name_mask": "*",
            "lower_bound": 0.0,
            "upper_bound": 0.0,
            "prev_msg_diff": 0,
            "merge": 0,
            "reversed": 0,
            "geozone_ids": "1,2,3",
            "type": 0,
            "min_speed": 45,
            "max_speed": 95,
            "include_lbs": 0,
            "lo": "",
        }

    def test_invalid_min_speed_adds_error(self):
        """Fails if an invalid min speed doesn't add an error to the form."""
        invalid_min_speed = 100
        data = self.valid_test_data.copy()
        data["min_speed"] = invalid_min_speed
        form = self.form_cls(data)
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form, "min_speed", "This value cannot be greater than 95, got 100."
        )

    def test_invalid_max_speed_adds_error(self):
        """Fails if an invalid max speed doesn't add an error to the form."""
        invalid_max_speed = 40
        data = self.valid_test_data.copy()
        data["max_speed"] = invalid_max_speed
        form = self.form_cls(data)
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form, "max_speed", "This value cannot be less than 45, got 40."
        )


class AddressTriggerFormTestCase(TestCase):
    def setUp(self) -> None:
        self.form_cls = AddressTriggerForm
        self.valid_test_data = {
            "sensor_type": WialonSensorType.ANY,
            "sensor_name_mask": "*",
            "lower_bound": 0.0,
            "upper_bound": 0.0,
            "prev_msg_diff": 0,
            "merge": 0,
            "reversed": 0,
            "radius": 300,
            "type": 0,
            "min_speed": 45,
            "max_speed": 95,
            "country": "USA",
            "region": "Texas",
            "city": "Cypress",
            "street": "South Dr",
            "house": "17610",
            "include_lbs": 0,
            "lo": "",
        }

    def test_invalid_min_speed_adds_error(self):
        """Fails if an invalid min speed doesn't add an error to the form."""
        invalid_min_speed = 100
        data = self.valid_test_data.copy()
        data["min_speed"] = invalid_min_speed
        form = self.form_cls(data)
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form, "min_speed", "This value cannot be greater than 95, got 100."
        )

    def test_invalid_max_speed_adds_error(self):
        """Fails if an invalid max speed doesn't add an error to the form."""
        invalid_max_speed = 40
        data = self.valid_test_data.copy()
        data["max_speed"] = invalid_max_speed
        form = self.form_cls(data)
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form, "max_speed", "This value cannot be less than 45, got 40."
        )


class SpeedTriggerFormTestCase(TestCase):
    def setUp(self) -> None:
        self.form_cls = SpeedTriggerForm
        self.valid_test_data = {
            "lower_bound": 0.0,
            "max_speed": 95,
            "merge": 0,
            "min_speed": 45,
            "prev_msg_diff": 0,
            "reversed": 0,
            "sensor_name_mask": "*",
            "sensor_type": WialonSensorType.ANY,
            "upper_bound": 0.0,
            "driver": 2,
        }

    def test_invalid_min_speed_adds_error(self):
        """Fails if an invalid min speed doesn't add an error to the form."""
        invalid_min_speed = 100
        data = self.valid_test_data.copy()
        data["min_speed"] = invalid_min_speed
        form = self.form_cls(data)
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form, "min_speed", "This value cannot be greater than 95, got 100."
        )

    def test_invalid_max_speed_adds_error(self):
        """Fails if an invalid max speed doesn't add an error to the form."""
        invalid_max_speed = 40
        data = self.valid_test_data.copy()
        data["max_speed"] = invalid_max_speed
        form = self.form_cls(data)
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form, "max_speed", "This value cannot be less than 45, got 40."
        )


class InterpositionTriggerFormTestCase(TestCase):
    def setUp(self) -> None:
        self.form_cls = GeofenceTriggerForm
        self.valid_test_data = {
            "sensor_name_mask": "*",
            "sensor_type": WialonSensorType.ANY,
            "lower_bound": 0.0,
            "upper_bound": 0.0,
            "merge": 0,
            "max_speed": 95,
            "min_speed": 45,
            "reversed": 0,
            "prev_msg_diff": 0,
            "radius": 100,
            "type": 0,
            "unit_guids": "1,2,3",
            "lo": "",
        }

    def test_invalid_min_speed_adds_error(self):
        """Fails if an invalid min speed doesn't add an error to the form."""
        invalid_min_speed = 100
        data = self.valid_test_data.copy()
        data["min_speed"] = invalid_min_speed
        form = self.form_cls(data)
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form, "min_speed", "This value cannot be greater than 95, got 100."
        )

    def test_invalid_max_speed_adds_error(self):
        """Fails if an invalid max speed doesn't add an error to the form."""
        invalid_max_speed = 40
        data = self.valid_test_data.copy()
        data["max_speed"] = invalid_max_speed
        form = self.form_cls(data)
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form, "max_speed", "This value cannot be less than 45, got 40."
        )
