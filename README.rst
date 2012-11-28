cartridge-stripe
================

Stripe_ credit card processing integration with Cartridge_.

.. _Cartridge: htps://cartridge.jupo.org
.. _Stripe: https://stripe.com/docs

==========
Install
==========

Follow the installation instructions of django-zebra_.

.. _django-zebra: https://github.com/GoodCloud/django-zebra#installation

::

    pip install cartridge-stripe

Update the settings.py to use your shiney new app.
Add it to 'INSTALLED_APPS' above 'cartridge.shop' to override the checkout template
or copy it to the templates dir in your project.

::

    INSTALLED_APPS = (
        # ...
        'cartridge_stripe',
        'cartridge.shop',
        # More stuff...
        )


    SHOP_HANDLER_PAYMENT = 'cartridge_stripe.payment_handler'
    SHOP_CHECKOUT_FORM_CLASS = 'cartridge_stripe.forms.OrderForm' 

=======
Style
=======

Add some sort of style for 'div.payment-errors' which will display validation
errors from stripe.

::

    div.payment-errors {
        color: #F00;
    }


=====
Done!
=====

Now your checkout flow should have card validation and the Stripe order number
linked to the purchase.

=====
Feedback
=====

I'm open to bugs and pull requests. Just run pep8 first.
Follow me and say hi!  https://twitter.com/readevalprint
