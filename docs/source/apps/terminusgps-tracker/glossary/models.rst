Models
======

.. py:class:: TrackerProfile

    Stores Wialon API data, Authorize.NET API data and user data.

    .. py:attribute:: user

        **Required**. The customer's Django user.
        
        *Assumes the Django user's username is a valid email address.*

        :type: :py:obj:`django.contrib.auth.models.AbstractBaseUser`


    .. py:attribute:: authorizenet_id

        An Authorize.NET ``customerProfileId``.

        :type: :py:obj:`int` | :py:obj:`None`
        :value: :py:obj:`None`


    .. py:attribute:: wialon_group_id

        The customer's Wialon group ID.

        :type: :py:obj:`int` | :py:obj:`None`
        :value: :py:obj:`None`


    .. py:attribute:: wialon_resource_id

        The customer's Wialon resource ID.

        :type: :py:obj:`int` | :py:obj:`None`
        :value: :py:obj:`None`


    .. py:attribute:: wialon_end_user_id

        The customer's Wialon user ID.

        :type: :py:obj:`int` | :py:obj:`None` 
        :value: :py:obj:`None`


    .. py:attribute:: wialon_super_user_id 

        The customer's super (owner) user ID.

        :type: :py:obj:`int` | :py:obj:`None`
        :value: :py:obj:`None`


.. py:class:: TrackerPaymentMethod

    .. py:attribute:: profile

        **Required**. A :py:obj:`TrackerProfile` associated with the payment method.

        :type: :py:obj:`TrackerProfile`

    .. py:attribute:: is_default

        Determines whether or not the payment method was set as default on creation with Authorize.NET.

        :type: :py:obj:`bool`
        :value: :py:obj:`False`

    .. py:attribute:: authorizenet_id

        The payment method's Authorize.NET ``customerPaymentProfileId``.

        :type: :py:obj:`int` | :py:obj:`None`
        :value: :py:obj:`None`


.. py:class:: TrackerShippingMethod

    .. py:attribute:: profile

        **Required**. A :py:obj:`TrackerProfile` associated with this shipping address.

        :type: :py:obj:`TrackerProfile`

    .. py:attribute:: is_default

        Determines whether or not this address was set as default on creation in Authorize.NET.

        :type: :py:obj:`bool`
        :value: :py:obj:`False`

    .. py:attribute:: authorizenet_id

        The shipping address' Authorize.NET ``customerPaymentProfileId``.

        :type: :py:obj:`int` | :py:obj:`None`
        :value: :py:obj:`None`


.. py:class:: TrackerSubscription

    .. py:attribute:: profile

        **Required**. A :py:class:`TrackerProfile` associated with this subscription.

        :type: :py:obj:`TrackerProfile`

    .. py:attribute:: authorizenet_id

        An Authorize.NET API ``subscriptionId``.

        :type: :py:obj:`int` | :py:obj:`None`
        :value: :py:obj:`None`

    .. py:attribute:: status

        The current Authorize.NET status of the subscription.

        +------------+------------------+--------------------------------------------------------------+
        | name       | value            | member                                                       |
        +============+==================+==============================================================+
        | Active     | ``"active"``     | :py:attr:`TrackerSubscription.SubscriptionStatus.ACTIVE`     |
        +------------+------------------+--------------------------------------------------------------+
        | Expired    | ``"expired"``    | :py:attr:`TrackerSubscription.SubscriptionStatus.EXPIRED`    |
        +------------+------------------+--------------------------------------------------------------+
        | Suspended  | ``"suspended"``  | :py:attr:`TrackerSubscription.SubscriptionStatus.SUSPENDED`  |
        +------------+------------------+--------------------------------------------------------------+
        | Canceled   | ``"canceled"``   | :py:attr:`TrackerSubscription.SubscriptionStatus.CANCELED`   |
        +------------+------------------+--------------------------------------------------------------+
        | Terminated | ``"terminated"`` | :py:attr:`TrackerSubscription.SubscriptionStatus.TERMINATED` | 
        +------------+------------------+--------------------------------------------------------------+

        :type: :py:obj:`str`
        :value: :py:attr:`TrackerSubscription.SubscriptionStatus.SUSPENDED`
        :canonical: :py:class:`TrackerSubscription.SubscriptionStatus`

    .. py:attribute:: tier

        The :py:obj:`TrackerSubscriptionTier` associated with this subscription.

        :type: :py:obj:`TrackerSubscriptionTier` | :py:obj:`None`
        :value: :py:obj:`None`


    .. py:method:: upgrade(new_tier, payment_id, address_id) -> None

        Upgrades the subscription to a new higher tier.

        :param new_tier: A new subscription tier to upgrade to.
        :type new_tier: :py:obj:`TrackerSubscriptionTier`
        :param payment_id: An Authorize.NET ``paymentProfileId``.
        :type payment_id: :py:obj:`int`
        :param address_id: An Authorize.NET ``customerAddressId``.
        :type address_id: :py:obj:`int`
        :returns: Nothing.
        :rtype: :py:obj:`None`
        :raises AssertionError: If the new subscription tier is lower than the current subscription tier.

    .. py:method:: downgrade(new_tier, payment_id, address_id) -> None

        Downgrades the subscription to a new lower tier.

        :param new_tier: A new subscription tier to downgrade to.
        :type new_tier: :py:obj:`TrackerSubscriptionTier`
        :param payment_id: An Authorize.NET ``paymentProfileId``.
        :type payment_id: :py:obj:`int`
        :param address_id: An Authorize.NET ``customerAddressId``.
        :type address_id: :py:obj:`int`
        :returns: Nothing.
        :rtype: :py:obj:`None`
        :raises AssertionError: If the new subscription tier is higher than the current subscription tier.

    .. py:method:: refresh_status() -> None

        Refreshes the subscription's status from Authorize.NET.

        :returns: Nothing.
        :rtype: :py:obj:`None`
        :raises AssertionError: If there is no subscription in Authorize.NET to refresh status.

    .. py:method:: cancel() -> None

        Cancels the Authorize.NET subscription.

        :returns: Nothing.
        :rtype: :py:obj:`None`
        :raises AssertionError: If there is no subscription in Authorize.NET to cancel.


.. py:class:: TrackerSubscription.SubscriptionStatus

    .. py:attribute:: ACTIVE

        The subscription is currently active.

        The subscription **IS** charging the user.

        :type: :py:obj:`str`
        :value: ``"active"``

    .. py:attribute:: EXPIRED

        The subscription has expired.

        The subscription **IS NOT** charging the user.

        :type: :py:obj:`str`
        :value: ``"expired"``

    .. py:attribute:: SUSPENDED

        The subscription has been suspended programatically.

        The subscription **IS NOT** charging the user.

        :type: :py:obj:`str`
        :value: ``"suspended"``

    .. py:attribute:: CANCELED

        The subscription has been canceled manually by the user.

        The subscription **IS NOT** charging the user.

        :type: :py:obj:`str`
        :value: ``"canceled"``

    .. py:attribute:: TERMINATED

        The subscription has been terminated by Authorize.NET.

        The subscription **IS NOT** charging the user.

        :type: :py:obj:`str`
        :value: ``"terminated"``


.. py:class:: TrackerSubscriptionTier

    .. py:attribute:: name

        Name of the subscription tier.

        :type: :py:obj:`str`

    .. py:attribute:: wialon_cmd

        Wialon command associated with the subscription tier.

        :type: :py:obj:`str` | :py:obj:`None`
        :value: :py:obj:`None`

    .. py:attribute:: wialon_id

        Wialon group associated with the subscription tier.

        :type: :py:obj:`int` | :py:obj:`None`
        :value: :py:obj:`None`

    .. py:attribute:: features

        Collection of features associated with this tier.

        :type: :py:type:`list[TrackerSubscriptionFeature]` | :py:obj:`None`
        :value: :py:obj:`None`

    .. py:attribute:: amount

        Amount of money (in USD) to be collected every period by this subscription tier.

        :type: :py:type:`Decimal`
        :value: ``0.00``

    .. py:attribute:: period

        How often the subscription charges the user.

        Represented by enum :py:class:`TrackerSubscriptionTier.IntervalPeriod`.

        +-----------+--------+-------------------------------------------------------------+
        | name      | value  | member                                                      |
        +===========+========+=============================================================+
        | Monthly   | ``1``  | :py:attr:`TrackerSubscriptionTier.IntervalPeriod.MONTHLY`   |
        +-----------+--------+-------------------------------------------------------------+
        | Quarterly | ``3``  | :py:attr:`TrackerSubscriptionTier.IntervalPeriod.QUARTERLY` |
        +-----------+--------+-------------------------------------------------------------+
        | Annually  | ``12`` | :py:attr:`TrackerSubscriptionTier.IntervalPeriod.ANNUALLY`  |
        +-----------+--------+-------------------------------------------------------------+

        :type: :py:obj:`int`
        :value: :py:attr:`TrackerSubscription.IntervalPeriod.MONTHLY`
        :canonical: :py:class:`TrackerSubscription.IntervalPeriod`

    .. py:attribute:: length

        How long the subscription charges the user.

        Represented by enum :py:class:`TrackerSubscriptionTier.IntervalLength`.

        +-----------+--------+-------------------------------------------------------------+
        | name      | value  | member                                                      |
        +===========+========+=============================================================+
        | Half year | ``6``  | :py:attr:`TrackerSubscriptionTier.IntervalLength.HALF_YEAR` |
        +-----------+--------+-------------------------------------------------------------+
        | Full year | ``12`` | :py:attr:`TrackerSubscriptionTier.IntervalLength.FULL_YEAR` |
        +-----------+--------+-------------------------------------------------------------+

        :type: :py:obj:`int`
        :value: :py:attr:`TrackerSubscription.IntervalLength.FULL_YEAR`
        :canonical: :py:class:`TrackerSubscription.IntervalLength`

    .. py:property:: group_name

        The name of the subscription's unit group in Wialon.

        :type: :py:obj:`str`
        :value: :py:attr:`~TrackerSubscriptionTier.name`  + ``" Subscription Group"``

    .. py:method:: wialon_add_to_group(unit_id, session) -> None

        Adds a Wialon unit to the subscription's Wialon Unit Group.

        :param unit_id: A Wialon unit ID that should be added to this tier's Wialon group.
        :param session: A valid Wialon API session.
        :type unit_id: :py:obj:`int`
        :type session: :py:type:`WialonSession`
        :rtype: :py:obj:`None`
        :return: Nothing.
        :raises ValueError: If the subscription tier does not have a Wialon group to add the unit to.

    .. py:method:: wialon_rm_from_group(unit_id, session) -> None

        Removes a Wialon unit from the subscription's Wialon Unit Group.

        :param unit_id: A Wialon unit ID that should be removed from this tier's Wialon group.
        :param session: A valid Wialon API session.
        :type unit_id: :py:obj:`int`
        :type session: :py:type:`WialonSession`
        :rtype: :py:obj:`None`
        :return: Nothing.
        :raises ValueError: If the subscription tier does not have a Wialon group to remove the unit from.
        :raises WialonError: If something goes wrong with the Wialon API.

    .. py:method:: wialon_create_subscription_group(owner_id, session) -> int

        Creates a Wialon Unit Group named after the subscription.

        :param owner_id: A Wialon user ID that will create the :py:obj:`~terminusgps_tracker.integrations.wialon.items.WialonUnitGroup`.
        :param session: A valid Wialon API session.
        :type owner_id: :py:obj:`int`
        :type session: :py:type:`~terminusgps_tracker.integrations.wialon.session.WialonSession`
        :rtype: :py:obj:`int`
        :return: The new Wialon Unit Group ID.
        :raises ValueError: If the Wialon Unit Group was not created properly.
        :raises WialonError: If something goes wrong with the Wialon API.

    .. py:method:: wialon_execute_subscription_command(unit_id, session, [timeout=5]) -> None

        Executes the subscription command on the Wialon unit by id.

        :param unit_id: A Wialon unit ID.
        :type unit_id: :py:obj:`int`
        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps_tracker.integrations.wialon.session.WialonSession`
        :param timeout: How long (in seconds) to attempt command execution before giving up. Default is 5.
        :type timeout: :py:obj:`int` = 5
        :return: Nothing.
        :rtype: :py:obj:`None`
        :raises WialonError: If something goes wrong with the Wialon API.

.. py:class:: TrackerSubscriptionTier.IntervalPeriod

    .. py:attribute:: MONTHLY

        A period that charges the user every month.

        :type: :py:obj:`int`
        :value: ``1``

    .. py:attribute:: QUARTERLY

        A period that charges the user every quarter (3 months).

        :type: :py:obj:`int`
        :value: ``3``

    .. py:attribute:: ANNUALLY

        A period that charges the user every year.

        :type: :py:obj:`int`
        :value: ``12``

.. py:class:: TrackerSubscriptionTier.IntervalLength

    .. py:attribute:: HALF_YEAR

        A subscription length of half a year (6 months).

        :type: :py:obj:`int`
        :value: ``6``

    .. py:attribute:: FULL_YEAR

        A subscription length of one full year (12 months).

        :type: :py:obj:`int`
        :value: ``12``


.. py:class:: TrackerSubscriptionFeature

    .. py:attribute:: name

        Human-readable representation of this subscription feature.

        Presented to the end-user.

        :type: :py:obj:`str`
        :value: ``""``

    .. py:attribute:: amount

        If present, rendered alongside this feature's name.

        +-----------+----------+---------------------------------------------------------+
        | name      | value    | member                                                  |
        +===========+==========+=========================================================+
        | None      | ``None`` | :py:obj:`None`                                          |
        +-----------+----------+---------------------------------------------------------+
        | Low       | ``5``    | :py:attr:`TrackerSubscriptionFeature.FeatureAmount.LOW` |
        +-----------+----------+---------------------------------------------------------+
        | Mid       | ``25``   | :py:attr:`TrackerSubscriptionFeature.FeatureAmount.MID` |
        +-----------+----------+---------------------------------------------------------+
        | Infinite  | ``999``  | :py:attr:`TrackerSubscriptionFeature.FeatureAmount.INF` |
        +-----------+----------+---------------------------------------------------------+

        :type: :py:obj:`int` | :py:obj:`None`
        :value: :py:obj:`None`
        :canonical: :py:class:`TrackerSubscriptionFeature.FeatureAmount`

.. py:class:: TrackerSubscriptionFeature.FeatureAmount

    .. py:attribute:: LOW

        :type: :py:obj:`int`
        :value: ``5``

    .. py:attribute:: MID

        :type: :py:obj:`int`
        :value: ``25``

    .. py:attribute:: INF

        :type: :py:obj:`int`
        :value: ``999``
