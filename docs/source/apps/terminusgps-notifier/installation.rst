Installation
============

============
Requirements
============

* `Python 3.1x`_
* `Twilio credentials`_
* `Wialon credentials`_

.. _Python 3.1x: https://www.python.org/downloads/
.. _Twilio credentials: https://www.twilio.com/login
.. _Wialon credentials: https://hosting.wialon.com/?lang=en

.. highlight:: bash

============
Instructions
============

1. Clone the `repository`_ and :command:`cd` into :literal:`terminusgps-notifier/`::

    git clone https://github.com/darthnall/terminusgps-notifier
    cd terminusgps-notifier/

.. _repository: https://github.com/darthnall/terminusgps-notifier

2. Set environment variables for the application::
   
    export TWILIO_TOKEN="<YOUR_TWILIO_TOKEN>"
    export TWILIO_SID="<YOUR_TWILIO_SID>"
    export TWILIO_MESSAGING_SID="<YOUR_TWILIO_MESSAGING_SID>"
    export TWILIO_FROM_NUMBER="<YOUR_TWILIO_FROM_NUMBER>"
    export WIALON_TOKEN="<YOUR_WIALON_TOKEN>"

3. Install dependencies::

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

4. Start the development server::

    fastapi dev

