from copy import copy
from itertools import dropwhile, takewhile
from locale import localeconv
from re import match

from django import forms
from django.utils.dates import MONTHS

from django.forms.models import BaseInlineFormSet, ModelFormMetaclass
from django.forms.models import inlineformset_factory
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import settings
from mezzanine.core.templatetags.mezzanine_tags import thumbnail
from django.utils.timezone import now

from cartridge.shop import checkout
from cartridge.shop.models import Product, ProductOption, ProductVariation
from cartridge.shop.models import Cart, CartItem, Order, DiscountCode
from cartridge.shop.utils import make_choices, set_locale, set_shipping


from zebra.conf import options
from zebra.widgets import NoNameSelect, NoNameTextInput
from zebra.forms import CardForm, StripePaymentForm
from cartridge.shop.forms import FormsetForm, DiscountForm


class OrderForm(FormsetForm, DiscountForm):
    """
    Main Form for the checkout process - ModelForm for the Order Model
    with extra fields for credit card. Used across each step of the
    checkout process with fields being hidden where applicable.
    """

    step = forms.IntegerField(widget=forms.HiddenInput())
    same_billing_shipping = forms.BooleanField(required=False, initial=True,
        label=_("My delivery details are the same as my billing details"))
    remember = forms.BooleanField(required=False, initial=True,
        label=_("Remember my address for next time"))
    card_name = forms.CharField(label=_("Cardholder name"))
    card_type = forms.ChoiceField(widget=forms.RadioSelect,
        choices=make_choices(settings.SHOP_CARD_TYPES))
    card_number = forms.CharField(required=False, max_length=20,
        widget=NoNameTextInput())
    card_cvv = forms.CharField(required=False, max_length=4,
        widget=NoNameTextInput())
    card_expiry_month = forms.ChoiceField(required=False, widget=NoNameSelect(),
        choices=MONTHS.iteritems())
    card_expiry_year = forms.ChoiceField(required=False, widget=NoNameSelect(),
        choices=options.ZEBRA_CARD_YEARS_CHOICES)
    last_4_digits = forms.CharField(required=True, min_length=4, max_length=4,
        widget=forms.HiddenInput())
    stripe_token = forms.CharField(required=True, widget=forms.HiddenInput())

    def addError(self, message):
        self._errors[NON_FIELD_ERRORS] = self.error_class([message])

    class Meta:
        model = Order
        fields = ([f.name for f in Order._meta.fields if
            f.name.startswith("billing_detail") or
            f.name.startswith("shipping_detail")] +
            ["additional_instructions", "discount_code"])



    def __init__(self, request, step, data=None, initial=None, errors=None):
        """
        Handle setting shipping field values to the same as billing
        field values in case JavaScript is disabled, hiding fields for
        the current step.
        """

        # Copy billing fields to shipping fields if "same" checked.
        first = step == checkout.CHECKOUT_STEP_FIRST
        last = step == checkout.CHECKOUT_STEP_LAST
        if (first and data is not None and "same_billing_shipping" in data):
            data = copy(data)
            # Prevent second copy occuring for forcing step below when
            # moving backwards in steps.
            data["step"] = step
            for field in data:
                billing = field.replace("shipping_detail", "billing_detail")
                if "shipping_detail" in field and billing in data:
                    data[field] = data[billing]

        if initial is not None:
            initial["step"] = step
        # Force the specified step in the posted data - this is
        # required to allow moving backwards in steps.
        if data is not None and int(data["step"]) != step:
            data = copy(data)
            data["step"] = step

        super(OrderForm, self).__init__(request, data=data, initial=initial)
        self._checkout_errors = errors
        settings.use_editable()
        # Hide Discount Code field if no codes are active.
        if (DiscountCode.objects.active().count() == 0 or
            not settings.SHOP_DISCOUNT_FIELD_IN_CHECKOUT):
            self.fields["discount_code"].widget = forms.HiddenInput()

        # Determine which sets of fields to hide for each checkout step.
        hidden = None
        if settings.SHOP_CHECKOUT_STEPS_SPLIT:
            if first:
                # Hide the cc fields for billing/shipping if steps are split.
                hidden = lambda f: (f.startswith("card_")
                                    or f == "stripe_token"
                                    or f == "last_4_digits")
            elif step == checkout.CHECKOUT_STEP_PAYMENT:
                # Hide the non-cc fields for payment if steps are split.
                hidden = lambda f: not (f.startswith("card_")
                                        or f == "stripe_token"
                                        or f == "last_4_digits")
        elif not settings.SHOP_PAYMENT_STEP_ENABLED:
            # Hide all the cc fields if payment step is not enabled.
            hidden = lambda f: (f.startswith("card_")
                                or f == "stripe_token"
                                or f == "last_4_digits")
        if settings.SHOP_CHECKOUT_STEPS_CONFIRMATION and last:
            # Hide all fields for the confirmation step.
            hidden = lambda f: True
        if hidden is not None:
            for field in self.fields:
                if hidden(field):
                    self.fields[field].widget = forms.HiddenInput()
                    self.fields[field].required = False

        # Set the choices for the cc expiry year relative to the current year.
        year = now().year
        choices = make_choices(range(year, year + 21))
        self.fields["card_expiry_year"].choices = choices

    def clean(self):
        """
        Raise ``ValidationError`` if any errors have been assigned
        externally, via one of the custom checkout step handlers.
        """
        if self._checkout_errors:
            raise forms.ValidationError(self._checkout_errors)
        return self.cleaned_data


