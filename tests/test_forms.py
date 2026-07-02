from django.test import TestCase

from terminusgps_notifier.forms import GeofenceTriggerForm, WialonSensorType


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
            "max_speed": 255,
            "include_lbs": 0,
            "lo": "",
        }

    def test_invalid_sensor_type_adds_error(self):
        """Fails if an invalid sensor type doesn't add an error to the form."""
        data = self.valid_test_data.copy()
        data["sensor_type"] = "not_a_sensor"
        form = self.form_cls(data)
        self.assertFalse(form.is_valid())
        self.assertFormError(
            form,
            "sensor_type",
            "Select a valid choice. not_a_sensor is not one of the available choices.",
        )
