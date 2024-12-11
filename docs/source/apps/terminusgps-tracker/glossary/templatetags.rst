Template Tags
=============

Add ``{% load terminusgps_tracker_display %}`` at the top of your template to use these tags.

.. py:function:: render_todo_item(todo, [size=6]) -> dict

    Takes a todo item and renders its value alongside an svg representing its completion status.

    :param todo: A :py:obj:`TodoItem` instance.
    :param size: Size of the returned svg, max of 96.
    :returns: A rendered todo item.
    :type todo: :py:class:`TodoItem`
    :type size: :py:type:`int`
    :rtype: :py:type:`dict`

.. py:function:: credit_card_icon(name, [size=6]) -> SafeString

    Takes a credit card merchant name and returns its icon svg, if it exists.

    Available credit card merchants:

        * `Visa <https://usa.visa.com/>`_
        * `Mastercard <https://www.mastercard.us/>`_
        * `Discover <https://www.discover.com/>`_
        * `American Express <https://www.americanexpress.com/>`_

    :param name: A credit card merchant name, i.e. ``"visa"``. Case insensitive.
    :param size: Size of the returned svg, max of 96.
    :returns: A credit card merchant icon.
    :type name: :py:type:`str`
    :type size: :py:type:`int`
    :rtype: :py:type:`django.utils.safestring.SafeString`

.. py:function:: social_media_icon(name, [size=6]) -> SafeString

    Takes a social media site name and returns its icon svg, if it exists.

    Available sites:

        * `Discord <https://discord.com/>`_
        * `Facebook <https://www.facebook.com/>`_
        * `Instagram <https://www.instagram.com/>`_
        * `Nextdoor <https://nextdoor.com/>`_
        * `Reddit <https://reddit.com/>`_
        * `TikTok <https://tiktok.com/>`_
        * `Twitter/X <https://x.com/>`_
        * `Youtube <https://youtube.com/>`_

    :param name: A social media site name, i.e. ``"instagram"``. Case insensitive.
    :param size: Size of the returned svg, max of 96.
    :returns: A social media site icon.
    :type name: :py:type:`str`
    :type size: :py:type:`int`
    :rtype: :py:type:`django.utils.safestring.SafeString`
