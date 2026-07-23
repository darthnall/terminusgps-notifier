import datetime
import decimal
import logging

from authorizenet import apicontractsv1, apicontrollers
from django.conf import settings
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import (
    AuthorizenetError,
    AuthorizenetService,
)

logger = logging.getLogger(__name__)


def get_subscription_contract(
    profile_id: str,
    address_id: str,
    payment_id: str,
    *,
    start_date: datetime.date | None = None,
    amount: decimal.Decimal = decimal.Decimal("60.00"),
    trial_amount: decimal.Decimal = decimal.Decimal("0.00"),
    total_occurrences: int = 9999,
    trial_occurrences: int = 0,
    interval_length: int = 1,
    interval_unit: str = "months",
) -> apicontractsv1.ARBSubscriptionType:
    interval = apicontractsv1.paymentScheduleTypeInterval()
    interval.length = interval_length
    interval.unit = interval_unit
    schedule = apicontractsv1.paymentScheduleType()
    schedule.interval = interval
    schedule.startDate = start_date or datetime.date.today()
    schedule.totalOccurrences = total_occurrences
    schedule.trialOccurrences = trial_occurrences
    profile = apicontractsv1.customerProfileIdType()
    profile.customerProfileId = profile_id
    profile.customerAddressId = address_id
    profile.customerPaymentProfileId = payment_id
    contract = apicontractsv1.ARBSubscriptionType()
    contract.paymentSchedule = schedule
    contract.profile = profile
    contract.amount = decimal.Decimal("60.00")
    contract.trialAmount = decimal.Decimal("0.00")
    return contract


def get_merchant_auth() -> apicontractsv1.merchantAuthenticationType:
    return apicontractsv1.merchantAuthenticationType(
        name=settings.MERCHANT_AUTH_LOGIN_ID,
        transactionKey=settings.MERCHANT_AUTH_TRANSACTION_KEY,
    )


def cancel_subscription(
    subscription_id: str, reference_id: str | None = None
) -> ObjectifiedElement:
    request = apicontractsv1.ARBCancelSubscriptionRequest()
    request.merchantAuthentication = get_merchant_auth()
    request.subscriptionId = subscription_id
    if reference_id is not None:
        request.refId = reference_id
    controller = apicontrollers.ARBCancelSubscriptionController(request)
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
    return response


def get_authorizenet_service() -> AuthorizenetService:
    """
    Returns an Authorizenet service object for safely interacting with the Authorizenet API.

    :returns: An Authorizenet service object.
    :rtype: :py:obj:`~terminusgps.authorizenet.service.AuthorizenetService`

    """
    return AuthorizenetService(
        login_id=settings.MERCHANT_AUTH_LOGIN_ID,
        transaction_key=settings.MERCHANT_AUTH_TRANSACTION_KEY,
        environment=settings.MERCHANT_AUTH_ENVIRONMENT,
    )


def get_hosted_profile_page_url() -> str:
    """Returns the Authorizenet hosted profile page URL."""
    return (
        "https://accept.authorize.net/customer/manage"
        if not settings.DEBUG
        else "https://test.authorize.net/customer/manage"
    )


def get_customer_profile_by_id(id: str) -> ObjectifiedElement:
    """
    Returns a customer profile from Authorizenet by id.

    :param id: An Authorizenet customer profile id.
    :type id: str
    :returns: A customer profile.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement`

    """
    service = get_authorizenet_service()
    return service.execute(
        api.get_customer_profile(customer_profile_id=int(id))
    )


def get_customer_profile(email: str) -> ObjectifiedElement:
    """
    Returns a customer profile from Authorizenet by email address.

    :param email: An email address.
    :type email: str
    :returns: A customer profile.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement`

    """
    service = get_authorizenet_service()
    return service.execute(api.get_customer_profile(email=email))


def create_customer_profile(
    email: str, merchant_id: str, description: str
) -> ObjectifiedElement:
    """
    Creates a customer profile from Authorizenet.

    If one already existed for the provided email, instead return the existing customer profile.

    :param email: An email address.
    :type email: str
    :param merchant_id: A merchant-designated customer id.
    :type merchant_id: str
    :param description: A short customer description.
    :type description: str
    :returns: A customer profile object.
    :rtype: :py:obj:`~lxml.objectify.ObjectifiedElement`

    """
    try:
        return get_customer_profile(email)
    except AuthorizenetError as error:
        if error.code != "E00040":  # Record not found
            raise

    contract = apicontractsv1.customerProfileType()
    contract.email = email
    contract.merchantCustomerId = merchant_id
    contract.description = description
    anet_service = get_authorizenet_service()
    anet_request = api.create_customer_profile(contract)
    return anet_service.execute(anet_request)
