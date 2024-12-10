Settings
========

===============
Django Settings
===============

:literal:`terminusgps-tracker` requires the following settings to be present in :literal:`settings.py`:


.. confval:: MERCHANT_AUTH_LOGIN_ID

   Used by Authorize.NET's API to authenticate the application.

   :type: :py:type:`str`
   :default: ``""``


.. confval:: MERCHANT_AUTH_TRANSACTION_KEY

   Used by Authorize.NET's API to sign transactions made by the application.

   :type: :py:type:`str`
   :default: ``""``


.. confval:: WIALON_TOKEN

   Used by Wialon's API to authenticate the application.

   :type: :py:type:`str`
   :default: ``""``


.. confval:: WIALON_HOST

   Wialon API host.

   :literal:`hst-api.wialon.com` works for most use cases.

   :type: :py:type:`str`
   :default: ``"hst-api.wialon.com"``


.. confval:: WIALON_ADMIN_ID

   Used by Wialon's API to create Wialon objects.

   :type: :py:type:`int` | :py:type:`None`
   :default: :py:type:`None`


.. confval:: WIALON_UNACTIVATED_GROUP

   Used by Wialon's API to validate IMEI numbers.

   **Wialon units not present in this group cannot be registered by the application.**

   :type: :py:type:`int` | :py:type:`None`
   :default: :py:type:`None`
