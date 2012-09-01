import logging
import cartridge
import stripe

from django.utils.translation import ugettext as _

logger = logging.getLogger(__name__)


class CheckoutError(Exception):
    """
    Should be raised in billing/shipping and payment handlers for
    cases such as an invalid shipping address or an unsuccessful
    payment.
    """
    pass


def billship_handler(request, order_form):
    from mezzanine.conf import settings
    from cartridge.shop.utils import set_shipping, sign
    settings.use_editable()
    set_shipping(request, _("Flat rate shipping"),
         settings.SHOP_DEFAULT_SHIPPING_VALUE)


def payment_handler(request, order_form, order):
    tok = order_form.cleaned_data['stripe_token']
    total = order.total
    try:
        charge = stripe.Charge.create(amount=int(total) * 100,
                                      currency="usd",
                                      card=tok,
                                      description=order)
        return charge.id

    except stripe.CardError as e:
        raise cartridge.shop.checkout.CheckoutError(e)



def order_handler(request, order_form, order):
    pass



