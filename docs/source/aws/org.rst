AWS Organizational Structure
==============================


=================
Top-level account
=================

Terminus GPS has one account, `admin-terminusgps`, that owns all AWS resources associated with Terminus GPS.

-----------------------------------
Logging in as the top-level account
-----------------------------------

To login to the top-level account, you can login to the `AWS console`_.

`NOTE: For most use cases, logging into an IAM workforce user is desired. Logging into the top-level account should not be a regular occurrence.`

.. _AWS console: https://aws.amazon.com/console/

=========================
IAM Identity Center Users
=========================

Terminus GPS utilizes `IAM Identity Center`_ to organize its users.

.. _IAM Identity Center: https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html

-----------------------------------------
Logging in as an IAM Identity Center user
-----------------------------------------

To login as an IAM Identity Center user, you can login to the `terminusgps-sso start page`_.

.. _terminusgps-sso start page: https://terminusgps.awsapps.com/start/


.. toctree::
   :maxdepth: 2
   :caption: Contents:
