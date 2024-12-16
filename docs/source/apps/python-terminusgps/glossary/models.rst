Models
======

.. py:class:: WialonBase

   :canonical: :py:class:`terminusgps.wialon.items.base.WialonBase`

   Stuff that everyone can do.


.. py:class:: WialonResource

    :canonical: :py:class:`terminusgps.wialon.items.resource.WialonResource`

    .. py:method:: create(owner_id, name) -> int | None

        :param owner_id: Owner user of the new Wialon resource.
        :type owner_id: :py:obj:`int`
        :param name: Name for the new Wialon resource.
        :type name: :py:obj:`str`
        :returns: A new Wialon resource's ID.
        :rtype: :py:obj:`int`


.. py:class:: WialonRetranslator

    :canonical: :py:class:`terminusgps.wialon.items.retranslator.WialonRetranslator`

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

    :canonical: :py:class:`terminusgps.wialon.items.route.WialonRoute`

    .. py:method:: create(owner_id, name) -> int | None

        :param owner_id: Owner user of the new Wialon route.
        :type owner_id: :py:obj:`int`
        :param name: Name for the new Wialon route.
        :type name: :py:obj:`str`
        :returns: A new Wialon route's ID.
        :rtype: :py:obj:`int`

.. py:class:: WialonUser

    :canonical: :py:class:`terminusgps.wialon.items.user.WialonUser`

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

    .. py:method:: assign_email(email) -> None

        Assigns an email address to the Wialon user.

        :param email: A valid email address.
        :type phone: :py:obj:`str`
        :returns: Nothing.
        :rtype: :py:obj:`None`
        :raises ValueError: If the email address is invalid.

.. py:class:: WialonUnitGroup

    :canonical: :py:class:`terminusgps.wialon.items.unit_group.WialonUnitGroup`

    .. py:method:: create(owner_id, name) -> int | None

        :param owner_id: Owner user of the new Wialon group.
        :type owner_id: :py:obj:`int`
        :param name: Name for the new Wialon group.
        :type name: :py:obj:`str`
        :returns: A new Wialon group's ID.
        :rtype: :py:obj:`int`

    .. py:method:: is_member(item) -> bool

        Checks if a Wialon item is a member of the group.

        :param item: A Wialon object.
        :type item: :py:obj:`~terminusgps.wialon.items.base.WialonBase`
        :returns: Whether or not ``item`` is a member of this group.
        :rtype: :py:obj:`bool`

    .. py:method:: grant_access(item, [access_mask=3540009843]) -> None

        Grants access to the group based on the access mask.

        :param item: A Wialon object to grant access to.
        :type item: :py:obj:`~terminusgps.wialon.items.base.WialonBase`
        :param access_mask: A Wialon access mask integer. Default is ``3540009843``.
        :type access_mask: :py:obj:`int`
        :returns: Nothing.
        :rtype: :py:obj:`None`

    .. py:method:: revoke_access(item) -> None

        Revokes access from the group.

        :param item: A Wialon object to revoke access from.
        :type item: :py:obj:`~terminusgps.wialon.items.base.WialonBase`
        :returns: Nothing.
        :rtype: :py:obj:`None`

    .. py:method:: add_item(item) -> None

        Adds ``item`` to the group.

        :param item: A Wialon object to add to the group.
        :type item: :py:obj:`~terminusgps.wialon.items.base.WialonBase`
        :returns: Nothing.
        :rtype: :py:obj:`None`

    .. py:method:: rm_item(item) -> None

        Removes ``item`` from the group.

        :param item: A Wialon object to remove from the group.
        :type item: :py:obj:`~terminusgps.wialon.items.base.WialonBase`
        :returns: Nothing.
        :rtype: :py:obj:`None`
        :raises AssertionError: If the item is not in the group.

    .. py:property:: items

        Calls the Wialon API and returns a list of the group's items.

        :type: :py:obj:`list`
        :rtype: :py:obj:`list[]`

.. py:class:: WialonUnit

    :canonical: :py:class:`terminusgps.wialon.items.unit.WialonUnit`

    .. py:method:: create(owner_id, name, hw_type) -> int | None

        :param owner_id: Owner user of the new Wialon unit.
        :type owner_id: :py:obj:`int`
        :param name: Name for the new Wialon unit.
        :type name: :py:obj:`str`
        :param hw_type: Hardware type for the new Wialon unit.
        :type str: :py:obj:`str`
        :returns: A new Wialon unit's ID.
        :rtype: :py:obj:`int`

    .. py:method:: execute_command(name, [link_type="", timeout=5, flags=0, param=None]) -> None

        :param name: A Wialon command name.
        :type name: :py:obj:`str`
        :param link_type: Protocol to use for command execution.
        :type link_type: :py:obj:`str`
        :param timeout: How long (in seconds) to wait before giving up on command execution.
        :type timeout: :py:obj:`int`
        :param flags: Additional flags to supply to the command's execution.
        :type flags: :py:obj:`int`
        :param param: Additional parameters to supply to the command's execution.
        :type param: :py:obj:`dict` | :py:obj:`None`
        :returns: Nothing.
        :rtype: :py:obj:`None`

    .. py:method:: set_access_password(password) -> None

        Sets the unit's access password to the supplied password.

        :param password: A new access password.
        :type password: :py:obj:`str`
        :returns: Nothing.
        :rtype: :py:obj:`None`

    .. py:method:: activate() -> None

        Activates the unit in Wialon.

        If already activated, does nothing.

        :returns: Nothing.
        :rtype: :py:obj:`None`

    .. py:method:: deactivate() -> None

        Deactivates the unit in Wialon.

        If already deactivated, does nothing.

        :returns: Nothing.
        :rtype: :py:obj:`None`
