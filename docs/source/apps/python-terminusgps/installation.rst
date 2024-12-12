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

---------------
Install via pip
---------------

Install the latest version:

.. code-block:: bash

   pip install terminusgps

Install a specific version:

.. code-block:: bash

   pip install terminusgps==1.0.0

Install the with development requirements:

.. code-block:: bash

   pip install 'terminusgps[dev]'

--------------
Install via uv
--------------

Add the package to the uv environment:

.. code-block:: bash

   uv add terminusgps

Add a specific version to the uv environment:

.. code-block:: bash

   uv add terminusgps==1.0.0

Add the development dependencies to the uv environment:

.. code-block:: bash

   uv add terminusgps --extra dev
