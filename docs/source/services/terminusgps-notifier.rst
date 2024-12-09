terminusgps-notifier
====================

`terminusgps-notifier`_ is a `FastAPI application`_ that uses the `Twilio API`_ to programatically create phone calls/sms messages.

**terminusgps-notifier** listens for webhooks at :literal:`/notify/<method>`.

.. _terminusgps-notifier: https://github.com/darthnall/terminusgps-notifier
.. _FastAPI application: https://fastapi.tiangolo.com/
.. _Twilio API: https://www.twilio.com/docs

============
Installation
============

.. highlight:: bash

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

------------
Requirements
------------

* `Python 3.1x`_
* `Twilio credentials`_
* `Wialon credentials`_

.. _Python 3.1x: https://www.python.org/downloads/
.. _Twilio credentials: https://www.twilio.com/login
.. _Wialon credentials: https://hosting.wialon.com/?lang=en

---------------------
Environment Variables
---------------------

Before using :literal:`terminusgps-notifier`, login to the above services and ensure you have the following values set in your project's environment:

.. confval:: TWILIO_TOKEN
   :type: ``str``
   :default: ``""``

    Twilio API token, used to authenticate with Twilio to make calls/sms.

.. confval:: TWILIO_SID
   :type: ``str``
   :default: ``""``

    Twilio Session ID, used to sign Twilio calls.

.. confval:: TWILIO_MESSAGING_SID
   :type: ``str``
   :default: ``""``

    Twilio Messaging Session ID, used to sign Twilio sms messages.

.. confval:: TWILIO_FROM_NUMBER
   :type: ``str``
   :default: ``""``

    Twilio from number, used as the origin phone number for this application's calls/sms messages.

.. confval:: WIALON_TOKEN
   :type: ``str``
   :default: ``""``

    Wialon API token, used to authenticate with Wialon's API to retrieve phone numbers from a unit.

=========
Reference
=========

.. py:class:: TwilioCaller

    Create :literal:`TwilioCaller` instances to use the Twilio API to make a call/send an sms message.

    .. py:method:: create_notification(self, to_number: str, message: str, method: str = "sms") -> Task[Any]
       :async:

        Creates an asyncronous notification task that must be awaited for execution.

.. py:function:: get_phone_numbers(to_number: str | None = None, unit_id: str | None = None) -> list[str]

   Takes either a :literal:`to_number` or a :literal:`unit_id` (or both) and returns a list of phone numbers associated with it (or both).

   If :literal:`unit_id` is supplied, the Wialon API is called to retrieve phone numbers out of that Wialon unit's custom fields (key=to_number).

.. py:function:: create_tasks(phone_numbers: list[str], message: str, method: str, caller: TwilioCaller) -> list[Task[Any]]

   Takes :literal:`phone_numbers`, a :literal:`message`, a :literal:`method` and a :literal:`TwilioCaller` instance, returns a list of awaitable Twilio notification tasks.

=====
Usage
=====

--------------
Twilio methods
--------------

**terminusgps-notifier** offers three types of notifications, text-to-speech phone calls, sms messaging and stdout.

For backwards compatibility, :literal:`call` and :literal:`phone` are both mapped to the same Twilio logic.

+--------+-------------+
| method | result      | 
+========+=============+
| call   | tts call    |
+--------+-------------+
| phone  | tts call    |
+--------+-------------+
| sms    | sms message |
+--------+-------------+
| echo   | stdout      |
+--------+-------------+

-----------------------
Notify one phone number
-----------------------

.. highlight:: python

Use the :literal:`create_notification()` method on a :literal:`TwilioCaller` instance to create an asyncronous notification task::

    import asyncio
    from asyncio import Task
    from caller import TwilioCaller

    to_number: str = "+15555555555"
    message: str = "This is a test message."
    method: str = "sms"
    caller: TwilioCaller = TwilioCaller()

    task: Task = caller.create_notification(
        to_number=to_number,
        message=message,
        method=method,
    )
    
After creating a task, execute it in :literal:`asyncio`'s event runner::

    asyncio.run(task)

-----------------------------
Notify multiple phone numbers
-----------------------------

Use the :literal:`create_tasks()` function with a list of phone numbers to create a list of awaitable tasks::

    import asyncio
    from asyncio import Task
    from typing import Any
    from caller import TwilioCaller

    phone_numbers: list[str] = [
        "+15555555555",
        "+17133049421",
        "+18324558034",
    ]
    message: str = "This is a test message."
    method: str = "sms"
    caller: TwilioCaller = TwilioCaller()

    tasks: list[Task[Any]] = create_tasks(
        phone_numbers,
        message=message,
        method="sms",
        caller=caller
    )
    
Execute the tasks using :literal:`asyncio.gather()`, unpacking the tasks with :literal:`*`::

        asyncio.gather(*tasks)
