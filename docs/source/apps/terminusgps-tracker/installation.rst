Installation
============

============
Requirements
============

* `Python 3.1x`_
* `uv v5.x`_
* `aws-cli-v2`_

.. _Python 3.1x: https://www.python.org/downloads/
.. _uv v5.x: https://docs.astral.sh/uv/
.. _aws-cli-v2: https://docs.aws.amazon.com/cli/

============
Instructions
============

1. Clone the `repository`_ and :command:`cd` into :literal:`terminusgps-site/`.

.. code-block:: bash

    git clone https://github.com/terminus-gps/terminusgps-site
    cd terminusgps-site/

.. _repository: https://github.com/terminus-gps/terminusgps-site

2. Login to the `AWS CLI v2`_.

.. code-block:: bash

   aws configure

.. _AWS CLI v2: https://docs.aws.amazon.com/cli/

3. Set the required :doc:`settings`.

.. code-block:: python

    # settings.py
    ...
    MERCHANT_AUTH_LOGIN_ID="<YOUR_AUTHORIZENET_LOGIN_ID>"
    MERCHANT_AUTH_TRANSACTION_KEY="<YOUR_AUTHORIZENET_TRANSACTION_KEY>"
    WIALON_TOKEN="<YOUR_MERCHANT_AUTH_LOGIN_ID>"
    WIALON_HOST="<YOUR_WIALON_HOST>" # Default is "hst-api.wialon.com"
    WIALON_ADMIN_ID="<YOUR_ADMIN_ID>"
    WIALON_UNACTIVATED_GROUP="<YOUR_UNACTIVATED_GROUP_ID>"


4. Install dependencies.

.. code-block:: bash

   uv sync --upgrade


5. Apply database migrations.

.. code-block:: bash

   uv run manage.py migrate


6. Start the development server.

.. code-block:: bash

   uv run manage.py runserver
