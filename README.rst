cartridge-stripe
================

Stripe_ credit card processing integration with Cartridge_.

.. _Cartridge: htps://cartridge.jupo.org
.. _Stripe: https://stripe.com/docs

==========
Install
==========

`pip install cartridge-stripe`

add to `INSTALLED_APPS` above `cartridge.shop` to override the checkout template
or copy it to your templates dir.

::

    INSTALLED_APPS = (
        # ...
        'cartridge_stripe',
        'cartridge.shop',
        # More stuff...
        )

