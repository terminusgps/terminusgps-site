Models
======

.. py:class:: WialonResource

    :canonical: :py:class:`terminusgps.items.base.WialonBase`

    .. py:method:: create(owner_id, name) -> int | None

        :param owner_id: Owner user of the new Wialon resource.
        :type owner_id: :py:obj:`int`
        :param name: Name for the new Wialon resource.
        :type name: :py:obj:`str`
        :returns: A new Wialon resource's ID.
        :rtype: :py:obj:`int`

.. py:class:: WialonRetranslator

    :canonical: :py:class:`terminusgps.items.base.WialonBase`

    .. py:method:: create(owner_id, name) -> int | None

        :param owner_id: Owner user of the new Wialon retranslator.
        :type owner_id: :py:obj:`int`
        :param name: Name for the new Wialon retranslator.
        :type name: :py:obj:`str`
        :param config: Configuration for the new retranslator.
        :type config: :py:obj:`dict`
        :returns: A new Wialon retranslator's ID.
        :rtype: :py:obj:`int`

.. py:class:: WialonRoute

    :canonical: :py:class:`terminusgps.items.base.WialonBase`

    .. py:method:: create(owner_id, name) -> int | None

        :param owner_id: Owner user of the new Wialon route.
        :type owner_id: :py:obj:`int`
        :param name: Name for the new Wialon route.
        :type name: :py:obj:`str`
        :returns: A new Wialon route's ID.
        :rtype: :py:obj:`int`

.. py:class:: WialonUser

    :canonical: :py:class:`terminusgps.items.base.WialonBase`

    .. py:method:: create(owner_id, name, password) -> int | None


        :param owner_id: Owner user of the new Wialon user.
        :type owner_id: :py:obj:`int`
        :param name: Name for the new Wialon user.
        :type name: :py:obj:`str`
        :param password: Password for the new Wialon user.
        :type password: :py:obj:`str`
        :returns: A new Wialon user's ID.
        :rtype: :py:obj:`int`
        :raises AssertionError: If the password is invalid.

    .. py:method:: has_access(other) -> bool

        Returns :py:obj:`True` if ``other`` is a Wialon object that this user has access to.

        :param other: A Wialon object.
        :type other: :py:obj:`~terminusgps.wialon.items.WialonBase`
        :returns: :py:obj:`True` if the user has access to ``other``, else :py:obj:`False`
        :rtype: :py:obj:`bool`

    .. py:method:: assign_phone(phone) -> None

        Assigns a phone number to the Wialon user.

        :param phone: A valid phone number, including country code.
        :type phone: :py:obj:`str`
        :returns: Nothing.
        :rtype: :py:obj:`None`
        :raises ValueError: If the phone number is invalid.
        :raises WialonError: If something goes wrong with the Wialon API.

    .. py:method:: assign_email(email) -> None

        Assigns an email address to the Wialon user.

        :param email: A valid email address.
        :type phone: :py:obj:`str`
        :returns: Nothing.
        :rtype: :py:obj:`None`
        :raises ValueError: If the email address is invalid.
        :raises WialonError: If something goes wrong with the Wialon API.

.. py:class:: WialonUnitGroup

    :canonical: :py:class:`terminusgps.items.base.WialonBase`

    .. py:method:: create(owner_id, name) -> int | None

        :param owner_id: Owner user of the new Wialon group.
        :type owner_id: :py:obj:`int`
        :param name: Name for the new Wialon group.
        :type name: :py:obj:`str`
        :returns: A new Wialon group's ID.
        :rtype: :py:obj:`int`

.. py:class:: WialonUnit

    :canonical: :py:class:`terminusgps.items.base.WialonBase`

    .. py:method:: create(owner_id, name, hw_type) -> int | None

        :param owner_id: Owner user of the new Wialon unit.
        :type owner_id: :py:obj:`int`
        :param name: Name for the new Wialon unit.
        :type name: :py:obj:`str`
        :param hw_type: Hardware type for the new Wialon unit.
        :type str: :py:obj:`str`
        :returns: A new Wialon unit's ID.
        :rtype: :py:obj:`int`
