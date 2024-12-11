Models
======

.. py:class:: TrackerProfile

    Stores Wialon API data, Authorize.NET API data and user data.

    .. py:attribute:: user

        The customer's Django user.
        
        *Assumes the Django user's username is a valid email address.*

        :type: :py:class:`django.contrib.auth.models.AbstractBaseUser`


    .. py:attribute:: authorizenet_id

        The customer's Authorize.NET ``customerProfileId``.

        :type: :py:type:`int` | :py:type:`None`
        :value: ``None``


    .. py:attribute:: wialon_group_id

        The customer's Wialon group ID.

        :type: :py:type:`int` | :py:type:`None`
        :value: ``None``


    .. py:attribute:: wialon_resource_id

        The customer's Wialon resource ID.

        :type: :py:type:`int` | :py:type:`None`
        :value: ``None``


    .. py:attribute:: wialon_end_user_id

        The customer's user ID.

        :type: :py:type:`int` | :py:type:`None` 
        :value: ``None``


    .. py:attribute:: wialon_super_user_id 

        The customer's super (owner) user ID.

        :type: :py:type:`int` | :py:type:`None`
        :value: ``None``


.. py:class:: TrackerPaymentMethod

    .. py:attribute:: is_default

        Determines whether or not the payment method was set as default on creation with Authorize.NET.

        :type: :py:type:`bool`
        :value: ``False``

    .. py:attribute:: authorizenet_id

        The payment method's Authorize.NET ``customerPaymentProfileId``.

        :type: :py:type:`int` | :py:type:`None`
        :value: ``None``

    .. py:attribute:: profile

        The :py:class:`TrackerProfile` associated with the payment method.

        :type: :py:class:`TrackerProfile`

.. py:class:: TrackerShippingMethod

    .. py:attribute:: is_default

        Determines whether or not this address was set as default on creation in Authorize.NET.

        :type: :py:type:`bool`
        :value: ``False``

    .. py:attribute:: authorizenet_id

        The shipping address' Authorize.NET ``customerPaymentProfileId``.

        :type: :py:type:`int` | :py:type:`None`
        :value: ``None``

    .. py:attribute:: profile

        The :py:class:`TrackerProfile` associated with this shipping address.

        :type: :py:class:`TrackerProfile`

.. py:class:: TrackerSubscription

    .. py:attribute:: status

        Current Authorize.NET status of the subscription.

        Represented by enum :py:class:`TrackerSubscription.SubscriptionStatus`.

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

        :type: :py:type:`str`
        :value: ``"suspended"``
        :canonical: :py:attr:`TrackerSubscription.SubscriptionStatus.SUSPENDED`

    .. py:attribute:: authorizenet_id

        An Authorize.NET API ``subscriptionId``.

        :type: :py:type:`int` | :py:type:`None`
        :value: ``None``

    .. py:attribute:: profile

        The :py:class:`TrackerProfile` associated with this subscription.

        :type: :py:class:`TrackerProfile`

    .. py:attribute:: tier

        The :py:class:`TrackerSubscriptionTier` associated with this subscription.

        :type: :py:class:`TrackerSubscriptionTier`


.. py:class:: TrackerSubscription.SubscriptionStatus

    .. py:attribute:: ACTIVE

        This subscription is currently active.

        This subscription **IS** charging the user.

        :type: :py:type:`str`
        :value: ``"active"``

    .. py:attribute:: EXPIRED

        This subscription has expired.

        This subscription **IS NOT** charging the user.

        :type: :py:type:`str`
        :value: ``"expired"``

    .. py:attribute:: SUSPENDED

        This subscription has been suspended programatically.

        This subscription **IS NOT** charging the user.

        :type: :py:type:`str`
        :value: ``"suspended"``

    .. py:attribute:: CANCELED

        This subscription has been canceled manually by the user.

        This subscription **IS NOT** charging the user.

        :type: :py:type:`str`
        :value: ``"canceled"``

    .. py:attribute:: TERMINATED

        This subscription has been terminated by Authorize.NET.

        This subscription **IS NOT** charging the user.

        :type: :py:type:`str`
        :value: ``"terminated"``


.. py:class:: TrackerSubscriptionTier

    .. py:attribute:: name

        Name of the subscription tier.

        :type: :py:type:`str`

    .. py:attribute:: wialon_cmd

        Wialon command associated with the subscription tier.

        :type: :py:type:`str`
        :value: ``""``

    .. py:attribute:: wialon_cmd_link

        Wialon command link to use when executing this tier's subscription command.

        Represented by enum :py:class:`TrackerSubscriptionTier.WialonCommandLink`.

        +---------+-----------+-----------------------------------------------------------+
        | name    | value     | member                                                    |
        +=========+===========+===========================================================+
        | Auto    | ``""``    | :py:attr:`TrackerSubscriptionTier.WialonCommandLink.AUTO` |
        +---------+-----------+-----------------------------------------------------------+
        | TCP     | ``"tcp"`` | :py:attr:`TrackerSubscriptionTier.WialonCommandLink.TCP`  |
        +---------+-----------+-----------------------------------------------------------+
        | UDP     | ``"udp"`` | :py:attr:`TrackerSubscriptionTier.WialonCommandLink.UDP`  |
        +---------+-----------+-----------------------------------------------------------+
        | Virtual | ``"vrt"`` | :py:attr:`TrackerSubscriptionTier.WialonCommandLink.VRT`  |
        +---------+-----------+-----------------------------------------------------------+
        | SMS     | ``"gsm"`` | :py:attr:`TrackerSubscriptionTier.WialonCommandLink.GSM`  |
        +---------+-----------+-----------------------------------------------------------+

        :type: :py:type:`str`
        :value: ``""``
        :canonical: :py:attr:`TrackerSubscriptionTier.WialonCommandLink.AUTO`

    .. py:attribute:: wialon_cmd_type

        Wialon command type to use when executing this tier's subscription command.

        Represented by enum :py:class:`TrackerSubscriptionTier.WialonCommandType`.

        +----------------------------+---------------------------+---------------------------------------------------------------------+
        | name                       | value                     | member                                                              |
        +============================+===========================+=====================================================================+
        | Block engine               | ``"block_engine"``        | :py:attr:`TrackerSubscriptionTier.WialonCommandType.ENGINE_BLOCK`   |
        +----------------------------+---------------------------+---------------------------------------------------------------------+
        | Unblock engine             | ``"unblock_engine"``      | :py:attr:`TrackerSubscriptionTier.WialonCommandType.ENGINE_UNBLOCK` |
        +----------------------------+---------------------------+---------------------------------------------------------------------+
        | Custom message             | ``"custom_msg"``          | :py:attr:`TrackerSubscriptionTier.WialonCommandType.MSG_CUSTOM`     |
        +----------------------------+---------------------------+---------------------------------------------------------------------+
        | Message to driver          | ``"driver_msg"``          | :py:attr:`TrackerSubscriptionTier.WialonCommandType.MSG_DRIVER`     |
        +----------------------------+---------------------------+---------------------------------------------------------------------+
        | Download messages          | ``"download_msgs"``       | :py:attr:`TrackerSubscriptionTier.WialonCommandType.MSG_DOWNLOAD`   |
        +----------------------------+---------------------------+---------------------------------------------------------------------+
        | Query position             | ``"query_pos"``           | :py:attr:`TrackerSubscriptionTier.WialonCommandType.QUERY_POS`      |
        +----------------------------+---------------------------+---------------------------------------------------------------------+
        | Query snapshot             | ``"query_photo"``         | :py:attr:`TrackerSubscriptionTier.WialonCommandType.QUERY_PHOTO`    |
        +----------------------------+---------------------------+---------------------------------------------------------------------+
        | Activate output            | ``"output_on"``           | :py:attr:`TrackerSubscriptionTier.WialonCommandType.OUTPUT_ON`      |
        +----------------------------+---------------------------+---------------------------------------------------------------------+
        | Deactivate output          | ``"output_off"``          | :py:attr:`TrackerSubscriptionTier.WialonCommandType.OUTPUT_OFF`     |
        +----------------------------+---------------------------+---------------------------------------------------------------------+
        | Send coordinates           | ``"send_position"``       | :py:attr:`TrackerSubscriptionTier.WialonCommandType.SEND_POS`       |
        +----------------------------+---------------------------+---------------------------------------------------------------------+
        | Set data transfer interval | ``"set_report_interval"`` | :py:attr:`TrackerSubscriptionTier.WialonCommandType.SET_REPORT_INT` |
        +----------------------------+---------------------------+---------------------------------------------------------------------+
        | Upload configuration       | ``"upload_cfg"``          | :py:attr:`TrackerSubscriptionTier.WialonCommandType.UPLOAD_CFG`     |
        +----------------------------+---------------------------+---------------------------------------------------------------------+
        | Upload firmware            | ``"upload_sw"``           | :py:attr:`TrackerSubscriptionTier.WialonCommandType.UPLOAD_SW`      |
        +----------------------------+---------------------------+---------------------------------------------------------------------+

        :type: :py:type:`str`
        :value: ``"upload_cfg"``
        :canonical: :py:attr:`TrackerSubscriptionTier.WialonCommandType.UPLOAD_CFG`

    .. py:attribute:: wialon_id

        Wialon group associated with the subscription tier.

        :type: :py:type:`int` | :py:type:`None`
        :value: ``None``

    .. py:attribute:: features

        Collection of features associated with this tier.

        :type: :py:type:`list[TrackerSubscriptionFeature]` | :py:type:`None`
        :value: ``None``

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

        :type: :py:type:`int`
        :value: ``1``
        :canonical: :py:attr:`TrackerSubscriptionTier.IntervalPeriod.MONTHLY`

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

        :type: :py:type:`int`
        :value: ``12``
        :canonical: :py:attr:`TrackerSubscriptionTier.IntervalLength.FULL_YEAR`

    .. py:method:: wialon_add_to_group(unit_id, session) -> None

        :param unit_id: A Wialon unit ID that should be added to this tier's Wialon group.
        :param session: A valid Wialon API session.
        :type unit_id: :py:type:`int`
        :type session: :py:type:`WialonSession`
        :rtype: :py:type:`None`
        :return: Nothing.
        :raises ValueError: If the subscription tier does not have a Wialon group to add the unit to.

    .. py:method:: wialon_rm_from_group(unit_id, session) -> None

        :param unit_id: A Wialon unit ID that should be removed from this tier's Wialon group.
        :param session: A valid Wialon API session.
        :type unit_id: :py:type:`int`
        :type session: :py:type:`WialonSession`
        :rtype: :py:type:`None`
        :return: Nothing.
        :raises ValueError: If the subscription tier does not have a Wialon group to remove the unit from.

.. py:class:: TrackerSubscriptionTier.IntervalPeriod

    .. py:attribute:: MONTHLY

        A period that charges the user every month.

        :type: :py:type:`int`
        :value: ``1``

    .. py:attribute:: QUARTERLY

        A period that charges the user every quarter (3 months).

        :type: :py:type:`int`
        :value: ``3``

    .. py:attribute:: ANNUALLY

        A period that charges the user every year.

        :type: :py:type:`int`
        :value: ``12``

.. py:class:: TrackerSubscriptionTier.IntervalLength

    .. py:attribute:: HALF_YEAR

        A subscription length of half a year (6 months).

        :type: :py:type:`int`
        :value: ``6``

    .. py:attribute:: FULL_YEAR

        A subscription length of one full year (12 months).

        :type: :py:type:`int`
        :value: ``12``

.. py:class:: TrackerSubscriptionTier.WialonCommandType

    .. py:attribute:: ENGINE_BLOCK

        :type: :py:type:`str`
        :value: ``"block_engine"``

    .. py:attribute:: ENGINE_UNBLOCK

        :type: :py:type:`str`
        :value: ``"unblock_engine"``

    .. py:attribute:: MSG_CUSTOM

        :type: :py:type:`str`
        :value: ``"custom_msg"``

    .. py:attribute:: MSG_DRIVER

        :type: :py:type:`str`
        :value: ``"driver_msg"``

    .. py:attribute:: MSG_DOWNLOAD

        :type: :py:type:`str`
        :value: ``"download_msgs"``

    .. py:attribute:: QUERY_POS

        :type: :py:type:`str`
        :value: ``"query_pos"``

    .. py:attribute:: QUERY_PHOTO

        :type: :py:type:`str`
        :value: ``"query_photo"``

    .. py:attribute:: OUTPUT_ON

        :type: :py:type:`str`
        :value: ``"output_on"``

    .. py:attribute:: OUTPUT_OFF

        :type: :py:type:`str`
        :value: ``"output_off"``

    .. py:attribute:: SEND_POS

        :type: :py:type:`str`
        :value: ``"send_position"``

    .. py:attribute:: SET_REPORT_INT

        :type: :py:type:`str`
        :value: ``"set_report_interval"``

    .. py:attribute:: UPLOAD_CFG

        :type: :py:type:`str`
        :value: ``"upload_cfg"``

    .. py:attribute:: UPLOAD_SW

        :type: :py:type:`str`
        :value: ``"upload_sw"``

.. py:class:: TrackerSubscriptionTier.WialonCommandLink

    .. py:attribute:: AUTO

        :type: :py:type:`str`
        :value: ``""``

    .. py:attribute:: TCP

        :type: :py:type:`str`
        :value: ``"tcp"``

    .. py:attribute:: UDP

        :type: :py:type:`str`
        :value: ``"udp"``

    .. py:attribute:: VRT

        :type: :py:type:`str`
        :value: ``"vrt"``

    .. py:attribute:: GSM

        :type: :py:type:`str`
        :value: ``"gsm"``


.. py:class:: TrackerSubscriptionFeature

    .. py:attribute:: name

        Human-readable representation of this subscription feature.

        Presented to the end-user.

        :type: :py:type:`str`
        :value: ``""``

    .. py:attribute:: amount

        If present, rendered alongside this feature's name.

        Represented by enum :py:class:`TrackerSubscriptionFeature.FeatureAmount`.

        +-----------+---------+---------------------------------------------------------+
        | name      | value   | member                                                  |
        +===========+=========+=========================================================+
        | Low       | ``5``   | :py:attr:`TrackerSubscriptionFeature.FeatureAmount.LOW` |
        +-----------+---------+---------------------------------------------------------+
        | Mid       | ``25``  | :py:attr:`TrackerSubscriptionFeature.FeatureAmount.MID` |
        +-----------+---------+---------------------------------------------------------+
        | Infinite  | ``999`` | :py:attr:`TrackerSubscriptionFeature.FeatureAmount.INF` |
        +-----------+---------+---------------------------------------------------------+

        :type: :py:type:`int` | :py:type:`None`
        :value: ``None``

.. py:class:: TrackerSubscriptionFeature.FeatureAmount

    .. py:attribute:: LOW

        :type: :py:type:`int`
        :value: ``5``

    .. py:attribute:: MID

        :type: :py:type:`int`
        :value: ``25``

    .. py:attribute:: INF

        :type: :py:type:`int`
        :value: ``999``


.. py:class:: TrackerTodoList

    .. py:attribute:: profile

        The :py:class:`TrackerProfile` associated with this todo list.

        :type: :py:class:`TrackerProfile`

.. py:class:: TodoItem

    .. py:attribute:: label

        Human-readable representation of this todo item.

        Presented to the end-user.

        :type: :py:type:`str`
        :value: ``""``

    .. py:attribute:: view

        The Django view associated with this todo item.

        :type: :py:type:`str`
        :value: ``""``

    .. py:attribute:: is_complete

        Determines whether or not this todo item is complete.

        :type: :py:type:`bool` 
        :value: ``False``

    .. py:attribute:: todo_list

        The todo list this todo item is associated with.

        :type: :py:class:`TrackerTodoList`
