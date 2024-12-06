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

.. _AWS console: https://aws.amazon.com/console/
.. [#f1] For most use cases, logging into an IAM Identity Center user is desired. Logging into the top-level account should not be a regular occurrence.

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
