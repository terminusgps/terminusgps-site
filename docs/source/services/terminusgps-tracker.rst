terminusgps-tracker
===================

`terminusgps-tracker`_ is a `Django application`_ that uses the `Wialon API`_ and the `Authorize.NET API`_ to manage user subscription plans, Wialon assets, and more.

.. _terminusgps-tracker: https://github.com/terminus-gps/terminusgps-site
.. _Django application: https://www.djangoproject.com/
.. _Wialon API: https://sdk.wialon.com/wiki/en/sidebar/remoteapi/apiref/apiref
.. _Authorize.NET API: https://developer.authorize.net/api/reference/index.html

============
Installation
============

1. Clone the `repository`_ and :command:`cd` into :literal:`terminusgps-site/`.

.. code-block:: bash

    git clone https://github.com/terminus-gps/terminusgps-site
    cd terminusgps-site/

.. _repository: https://github.com/terminus-gps/terminusgps-site

2. Login to the `AWS CLI v2`_.

.. code-block:: bash

   aws configure

.. _AWS CLI v2: https://docs.aws.amazon.com/cli/

3. Install dependencies.

.. code-block:: bash

   uv sync --upgrade


4. Apply database migrations.

.. code-block:: bash

   uv run manage.py migrate


5. Start the development server.

.. code-block:: bash

   uv run manage.py runserver

------------
Requirements
------------

* `Python 3.1x`_
* `uv v5.x`_
* `aws-cli-v2`_

.. _Python 3.1x: https://www.python.org/downloads/
.. _uv v5.x: https://docs.astral.sh/uv/
.. _aws-cli-v2: https://docs.aws.amazon.com/cli/

---------------
Django Settings
---------------

:literal:`terminusgps-tracker` requires the following settings to be present in :literal:`settings.py`:

.. confval:: MERCHANT_AUTH_LOGIN_ID
   :type: ``str``
   :default: ``""``

   Used by Authorize.NET's API to authenticate the application.

.. confval:: MERCHANT_AUTH_TRANSACTION_KEY
   :type: ``str``
   :default: ``""``

   Used by Authorize.NET's API to sign transactions made by the application.

.. confval:: WIALON_TOKEN
   :type: ``str``
   :default: ``""``

   Used by Wialon's API to authenticate the application.

.. confval:: WIALON_HOST
   :type: ``str``
   :default: ``"hst-api.wialon.com"``

   Wialon API host.

   :literal:`hst-api.wialon.com` works for most use cases.

.. confval:: WIALON_ADMIN_ID
   :type: ``int | None``
   :default: ``None``

   Used by Wialon's API to create Wialon objects.

.. confval:: WIALON_UNACTIVATED_GROUP
   :type: ``int | None``
   :default: ``None``

   Used by Wialon's API to validate IMEI numbers.

   **Wialon units not present in this group cannot be registered by the application.**

=========
Reference
=========

------
Models
------


.. py:class:: TrackerProfile

    Stores Wialon API data, Authorize.NET API data and user data.

    .. py:attribute:: user
        :type: django.contrib.auth.models.AbstractBaseUser
        :value: django.contrib.auth.get_user_model()

        A Django user.
        
        Assumes :literal:`TrackerProfile.user.username` is a valid email address.

    .. py:attribute:: authorizenet_id
        :type: int | None
        :value: None

        Authorize.NET :literal:`customerProfileId`.

    .. py:attribute:: wialon_group_id
        :type: int | None
        :value: None

        Wialon group id associated with this profile.

    .. py:attribute:: wialon_resource_id
        :type: int | None
        :value: None

        Wialon resource id associated with this profile.

    .. py:attribute:: wialon_end_user_id
        :type: int | None
        :value: None

        Wialon end user id associated with this profile.

    .. py:attribute:: wialon_super_user_id 
        :type: int | None
        :value: None

        Wialon super user id associated with this profile.

.. py:class:: TrackerPaymentMethod

    .. py:attribute:: is_default
        :type: bool
        :value: False

    .. py:attribute:: authorizenet_id
        :type: int | None
        :value: None

    .. py:attribute:: profile
        :type: TrackerProfile

.. py:class:: TrackerShippingMethod

    .. py:attribute:: is_default
        :type: bool
        :value: False

    .. py:attribute:: authorizenet_id
        :type: int | None
        :value: None

    .. py:attribute:: profile
        :type: TrackerProfile

.. py:class:: TrackerSubscription

    .. py:attribute:: status
        :type: str
        :value: Suspended

    .. py:attribute:: authorizenet_id
        :type: int | None
        :value: None

    .. py:attribute:: profile
        :type: TrackerProfile

    .. py:attribute:: tier
        :type: TrackerSubscriptionTier


---------------
Data Structures
---------------

.. py:class:: TrackerSubscriptionFeature

    .. py:attribute:: name
        :type: str

    .. py:attribute:: wialon_id
        :type: int | None
        :value: None

    .. py:attribute:: wialon_cmd
        :type: int | None
        :value: None

    .. py:attribute:: wialon_cmd_link
        :type: int | None
        :value: None

    .. py:attribute:: wialon_cmd_type
        :type: int | None
        :value: None

    .. py:attribute:: features
        :type: list[TrackerSubscriptionFeature]

    .. py:attribute:: amount
        :type: Decimal
        :value: 0.00

    .. py:attribute:: period
        :type: int
        :value: 1

    .. py:attribute:: length
        :type: int
        :value: 12

.. py:class:: TrackerSubscriptionFeature

    .. py:attribute:: name
        :type: str
        :value: ""

    .. py:attribute:: amount
        :type: int | None
        :value: None

.. py:class:: FeatureAmount
  
    .. py:attribute:: LOW
        :type: int
        :value: 5

    .. py:attribute:: MID
        :type: int
        :value: 25

    .. py:attribute:: INF
        :type: int
        :value: 999 

.. py:class:: TodoItem

    .. py:attribute:: todo_list
        :type: TodoList

    .. py:attribute:: label
        :type: str
        :value: ""

    .. py:attribute:: view
        :type: str
        :value: ""

    .. py:attribute:: is_complete
        :type: bool
        :value: False
