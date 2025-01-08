Registration Flow
=================

1. `token_login`_

    Login with token generated from Admin Token account, operate as Terminus-1000

    +---------------+---------------------------------------------------------------------------------------+
    | Parameter     | Value                                                                                 |
    +===============+=======================================================================================+
    | ``token``     | :py:data:`11800cd0b79970ba0731dd315341010017672A78226A55AE9746D57F7457B8B79C760AD5`   |
    +---------------+---------------------------------------------------------------------------------------+
    | ``operateAs`` | :py:data:`27881459`                                                                   |
    +---------------+---------------------------------------------------------------------------------------+
    | ``fl``        | :py:data:`0x3`                                                                        |
    +---------------+---------------------------------------------------------------------------------------+

2. `core_create_resource`_

    Create resource #1111111.

    +----------------------+------------------------------------------------+
    | Parameter            | Value                                          |
    +======================+================================================+
    | ``creatorId``        | :py:data:`27881459`                            |
    +----------------------+------------------------------------------------+
    | ``name``             | :py:data:`account_dylanlifemancer@gmail.com`   |
    +----------------------+------------------------------------------------+
    | ``dataFlags``        | :py:data:`0x1`                                 |
    +----------------------+------------------------------------------------+
    | ``skipCreatorCheck`` | :py:data:`1`                                   |
    +----------------------+------------------------------------------------+

3. `core_search_item`_

    Search for item #1111111.

    +---------------+--------------------+
    | Parameter     | Value              |
    +===============+====================+
    | ``id``        | :py:data:`1111111` |
    +---------------+--------------------+
    | ``fl``        | :py:data:`0x1`     |
    +---------------+--------------------+

4. `core_create_user`_

    Create user #2222222.

    +----------------------+------------------------------------------------+
    | Parameter            | Value                                          |
    +======================+================================================+
    | ``creatorId``        | :py:data:`27881459`                            |
    +----------------------+------------------------------------------------+
    | ``name``             | :py:data:`account_dylanlifemancer@gmail.com`   |
    +----------------------+------------------------------------------------+
    | ``password``         | :py:data:`Terminus#1`                          |
    +----------------------+------------------------------------------------+


5. `core_search_item`_

    Search for item #2222222.

    +---------------+--------------------+
    | Parameter     | Value              |
    +===============+====================+
    | ``id``        | :py:data:`2222222` |
    +---------------+--------------------+
    | ``fl``        | :py:data:`0x1`     |
    +---------------+--------------------+

6. `core_create_user`_

    Create user #3333333.

    +----------------------+--------------------------------------+
    | Parameter            | Value                                |
    +======================+======================================+
    | ``creatorId``        | :py:data:`27881459`                  |
    +----------------------+--------------------------------------+
    | ``name``             | :py:data:`dylanlifemancer@gmail.com` |
    +----------------------+--------------------------------------+
    | ``password``         | :py:data:`Terminus#1`                |
    +----------------------+--------------------------------------+

7. `core_search_item`_

    Search for item #3333333.

    +---------------+--------------------+
    | Parameter     | Value              |
    +===============+====================+
    | ``id``        | :py:data:`3333333` |
    +---------------+--------------------+
    | ``fl``        | :py:data:`0x1`     |
    +---------------+--------------------+

8. `core_create_unit_group`_

    Create unit group #4444444.

    +----------------------+--------------------------------------------+
    | Parameter            | Value                                      |
    +======================+============================================+
    | ``creatorId``        | :py:data:`27881459`                        |
    +----------------------+--------------------------------------------+
    | ``name``             | :py:data:`group_dylanlifemancer@gmail.com` |
    +----------------------+--------------------------------------------+
    | ``password``         | :py:data:`Terminus#1`                      |
    +----------------------+--------------------------------------------+

9. `core_search_item`_

    Search for item #4444444.

    +---------------+--------------------+
    | Parameter     | Value              |
    +===============+====================+
    | ``id``        | :py:data:`4444444` |
    +---------------+--------------------+
    | ``fl``        | :py:data:`0x1`     |
    +---------------+--------------------+

10. `account_create_account`_

    Create account from #1111111.

    +------------+---------------------------------+
    | Parameter  | Value                           |
    +============+=================================+
    | ``itemId`` | :py:data:`1111111`              |
    +------------+---------------------------------+
    | ``plan``   | :py:data:`terminusgps_ext_hist` |
    +------------+---------------------------------+

11. `account_enable_account`_

    Enable account from #1111111.

    +------------+--------------------+
    | Parameter  | Value              |
    +============+====================+
    | ``itemId`` | :py:data:`1111111` |
    +------------+--------------------+
    | ``enable`` | :py:data:`1`       |
    +------------+--------------------+

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
