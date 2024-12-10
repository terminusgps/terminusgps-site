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

3. Install dependencies.

.. code-block:: bash

   uv sync --upgrade


4. Apply database migrations.

.. code-block:: bash

   uv run manage.py migrate


5. Start the development server.

.. code-block:: bash

   uv run manage.py runserver
