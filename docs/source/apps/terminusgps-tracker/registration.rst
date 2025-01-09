Registration Flow
=================

By the end of registration, we will create the following objects using Wialon's API:

+--------------+------------+-----------------------------------+
| ID           | Type       | Name                              |
+==============+============+===================================+
| ``11111111`` | Resource   | account_dylanlifemancer@gmail.com |
+--------------+------------+-----------------------------------+
| ``22222222`` | User       | account_dylanlifemancer@gmail.com |
+--------------+------------+-----------------------------------+
| ``33333333`` | User       | dylanlifemancer@gmail.com         |
+--------------+------------+-----------------------------------+
| ``44444444`` | Unit Group | group_dylanlifemancer@gmail.com   |
+--------------+------------+-----------------------------------+

1. `token_login`_

    To create a Wialon API session, we call `token_login`_.

    This logs in to the Wialon API and starts a new session.

    +---------------+---------------------------------------------------------------------------------------+
    | Parameter     | Value                                                                                 |
    +===============+=======================================================================================+
    | ``token``     | :confval:`WIALON_TOKEN`                                                               |
    +---------------+---------------------------------------------------------------------------------------+
    | ``operateAs`` | :confval:`WIALON_ADMIN_ID`                                                            |
    +---------------+---------------------------------------------------------------------------------------+
    | ``fl``        | :py:data:`0x3`                                                                        |
    +---------------+---------------------------------------------------------------------------------------+

2. `core_create_user`_

    First we make the account user, "account_dylanlifemancer@gmail.com".

    The password is usually user input.

    +----------------------+------------------------------------------------+
    | Parameter            | Value                                          |
    +======================+================================================+
    | ``creatorId``        | :confval:`WIALON_ADMIN_ID`                     |
    +----------------------+------------------------------------------------+
    | ``name``             | :py:data:`account_dylanlifemancer@gmail.com`   |
    +----------------------+------------------------------------------------+
    | ``password``         | :py:data:`Terminus#1`                          |
    +----------------------+------------------------------------------------+

3. `core_search_item`_

    After creating objects using :py:mod:`~terminusgps.wialon`, we must call `core_search_item`_.

    This will call the Wialon API to populate data in our :py:obj:`~terminusgps.wialon.items.WialonUser` object.

    +---------------+---------------------+
    | Parameter     | Value               |
    +===============+=====================+
    | ``id``        | :py:data:`22222222` |
    +---------------+---------------------+
    | ``fl``        | :py:data:`0x1`      |
    +---------------+---------------------+

4. `core_create_resource`_

    Next, we create the Wialon resource that will act as an account, by calling `core_create_resource`_.

    The creator of this resource is the (account_dylanlifemancer@gmail.com) user we created earlier.

    The resource and the user are named the same.

    +----------------------+-------------------------------------------------+
    | Parameter            | Value                                           |
    +======================+=================================================+
    | ``creatorId``        | :py:data:`22222222`                             |
    +----------------------+-------------------------------------------------+
    | ``name``             | :py:data:`account_dylanlifemancer@gmail.com`    |
    +----------------------+-------------------------------------------------+
    | ``dataFlags``        | :py:data:`0x1`                                  |
    +----------------------+-------------------------------------------------+
    | ``skipCreatorCheck`` | :py:data:`1`                                    |
    +----------------------+-------------------------------------------------+

5. `core_search_item`_

    Call the Wialon API to populate data in our :py:obj:`~terminusgps.wialon.items.WialonResource` object.

    +---------------+---------------------+
    | Parameter     | Value               |
    +===============+=====================+
    | ``id``        | :py:data:`11111111` |
    +---------------+---------------------+
    | ``fl``        | :py:data:`0x1`      |
    +---------------+---------------------+

6. `core_create_user`_

    Next, we create the end user. The end user is created by our admin user, NOT the account user.

    Our end user will operate as (login as) this user to interact with Terminus GPS services.

    +----------------------+--------------------------------------+
    | Parameter            | Value                                |
    +======================+======================================+
    | ``creatorId``        | :confval:`WIALON_ADMIN_ID`           |
    +----------------------+--------------------------------------+
    | ``name``             | :py:data:`dylanlifemancer@gmail.com` |
    +----------------------+--------------------------------------+
    | ``password``         | :py:data:`Terminus#1`                |
    +----------------------+--------------------------------------+

7. `core_search_item`_

    Call the Wialon API to populate data in our :py:obj:`~terminusgps.wialon.items.WialonUser` object.

    +---------------+---------------------+
    | Parameter     | Value               |
    +===============+=====================+
    | ``id``        | :py:data:`33333333` |
    +---------------+---------------------+
    | ``fl``        | :py:data:`0x1`      |
    +---------------+---------------------+

8. `core_create_unit_group`_

    Next, we create a unit group for the new account. This group should be created by the admin user, NOT the account user.

    This unit group is intended for mass command execution convenience, e.g. subscription commands, enabling/disabling.

    +----------------------+--------------------------------------------+
    | Parameter            | Value                                      |
    +======================+============================================+
    | ``creatorId``        | :confval:`WIALON_ADMIN_ID`                 |
    +----------------------+--------------------------------------------+
    | ``name``             | :py:data:`group_dylanlifemancer@gmail.com` |
    +----------------------+--------------------------------------------+
    | ``password``         | :py:data:`Terminus#1`                      |
    +----------------------+--------------------------------------------+

9. `core_search_item`_

    Call the Wialon API to populate data in our :py:obj:`~terminusgps.wialon.items.WialonUnitGroup` object.

    +---------------+---------------------+
    | Parameter     | Value               |
    +===============+=====================+
    | ``id``        | :py:data:`44444444` |
    +---------------+---------------------+
    | ``fl``        | :py:data:`0x1`      |
    +---------------+---------------------+

10. `account_create_account`_

    Next, we call `account_create_account`_ to create an actual Wialon account.

    Wialon accounts require a user and a resource, with the caveat that the intended account user cannot be the creator of Wialon other objects.

    This is why we created the other objects under the admin user, rather than the account user.

    +------------+----------------------------------+
    | Parameter  | Value                            |
    +============+==================================+
    | ``itemId`` | :py:data:`11111111`              |
    +------------+----------------------------------+
    | ``plan``   | :py:data:`terminusgps_ext_hist`  |
    +------------+----------------------------------+

11. `account_enable_account`_

    Finally, we enable the new account with `account_enable_account`_.

    +------------+---------------------+
    | Parameter  | Value               |
    +============+=====================+
    | ``itemId`` | :py:data:`11111111` |
    +------------+---------------------+
    | ``enable`` | :py:data:`1`        |
    +------------+---------------------+

=====
Views
=====

1. GET :literal:`/signup/`

    Gets the signup form.

2. POST :literal:`/signup/`

    Submits the signup form.

3. GET :literal:`/profile/`

    Gets the user's profile.


====================
Wialon API Endpoints
====================

+---------------------------+
| Name                      |
+===========================+
| `token_login`_            |
+---------------------------+
| `core_search_item`_       |
+---------------------------+
| `core_create_resource`_   |
+---------------------------+
| `core_create_user`_       |
+---------------------------+
| `core_create_unit_group`_ |
+---------------------------+
| `account_create_account`_ |
+---------------------------+
| `account_enable_account`_ |
+---------------------------+

.. _token_login: https://sdk.wialon.com/wiki/en/sidebar/remoteapi/apiref/token/login
.. _core_search_item: https://sdk.wialon.com/wiki/en/sidebar/remoteapi/apiref/core/search_item
.. _core_create_resource: https://sdk.wialon.com/wiki/en/sidebar/remoteapi/apiref/core/create_resource
.. _core_create_unit_group: https://sdk.wialon.com/wiki/en/sidebar/remoteapi/apiref/core/create_unit_group
.. _core_create_user: https://sdk.wialon.com/wiki/en/sidebar/remoteapi/apiref/core/create_user
.. _account_create_account: https://sdk.wialon.com/wiki/en/sidebar/remoteapi/apiref/account/create_account
.. _account_enable_account: https://sdk.wialon.com/wiki/en/sidebar/remoteapi/apiref/account/enable_account
