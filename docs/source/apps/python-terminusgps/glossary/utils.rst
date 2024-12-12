Utilities
=========

.. py:function:: is_unique(value, session, [items_type="avl_unit"]) -> bool

    :param value: The value to check.
    :type value: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :returns: Whether or not ``value`` is unique in the Wialon database.
    :rtype bool: :py:obj:`bool`

.. py:function:: gen_wialon_password([length=16]) -> str

    Generates a Wialon compliant password.

    **Password Requirements**

    * Minimum 4 characters.
    * Maximum 64 characters.
    * **DOES** contain at least one uppercase letter.
    * **DOES** contain at least one lowercase letter.
    * **DOES** contain at least one digit.
    * **DOES** contain at least one special symbol.
    * **DOES NOT** contain at least one forbidden symbol.

    **Allowed special symbols**

    ``! @ # $ % ^ * ( ) [ ] - _ +``

    **Forbidden symbols**

    ``, : & < > '``

    :param length: The length of the password. Default is 16.
    :type length: :py:obj:`int`
    :returns: A new Wialon compliant password.
    :rtype: :py:obj:`str`
