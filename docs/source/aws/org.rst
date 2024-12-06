Organization Structure
======================


=================
Top-level account
=================

Terminus GPS has one account, `admin-terminusgps`, that owns all AWS resources associated with Terminus GPS.

-----------------------------------
Logging in as the top-level account
-----------------------------------

To login to the top-level account [#f1]_, you can login to the `AWS console`_.

Unless it's an emergency, please login as an IAM Identity Center user instead.

.. _AWS console: https://aws.amazon.com/console/
.. [#f1] For most use cases, logging into as an IAM Identity Center user is desired. Logging into the top-level account should not be a regular occurrence.

=========================
IAM Identity Center Users
=========================

Terminus GPS utilizes `IAM Identity Center`_ to organize its users.

Logging in as one of these users allows Terminus GPS staff to temporarily elevate their permissions to `admin-terminusgps`'s level.

.. _IAM Identity Center: https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html

-----------------------------------------
Logging in as an IAM Identity Center user
-----------------------------------------

To login as an IAM Identity Center user, you can login to the `terminusgps-sso start page`_.

.. _terminusgps-sso start page: https://terminusgps.awsapps.com/start/

------------------------------
IAM Identity Center User Roles
------------------------------

Depending on the user, the following roles may or may not be available for selection.

^^^^^^^^^^^^^^^^^^^
AdministratorAccess
^^^^^^^^^^^^^^^^^^^

Full access to the AWS account.

**DO NOT** use this role unless you are manipulating IAM Identity Center.

^^^^^^^
Billing
^^^^^^^

Access to the AWS account's billing information, including the ability to update/delete payment methods.

^^^^^^^^^^^^^^^
PowerUserAccess
^^^^^^^^^^^^^^^

Full access to the AWS account `except` for IAM Identity Center.

^^^^^^^^^^^^^^
ViewOnlyAccess
^^^^^^^^^^^^^^

Full access to the AWS account `except` for IAM Identity Center and Billing.
