import cartridge
import stripe

from django.utils.translation import ugettext as _


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
