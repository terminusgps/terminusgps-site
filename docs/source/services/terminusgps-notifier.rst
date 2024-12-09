terminusgps-notifier
====================

`terminusgps-notifier`_ is a `FastAPI application`_ that uses the `Twilio API`_ to programatically create phone calls/sms messages.

.. _terminusgps-notifier: https://github.com/darthnall/terminusgps-notifier
.. _FastAPI application: https://fastapi.tiangolo.com/
.. _Twilio API: https://www.twilio.com/docs

============
Installation
============

------------
Requirements
------------

* `UNIX-like command-line interface`_
* `Python 3.1x`_
* `Twilio credentials`_
* `Wialon credentials`_

.. _UNIX-like command-line interface: https://en.wikipedia.org/wiki/Unix_shell
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

.. py:function:: create_tasks(phone_numbers: list[str], message: str, method: str, caller: TwilioCaller) -> list[Task[Any]]

   Takes :literal:`phone_numbers`, a :literal:`message`, and a :literal:`method` and returns a list of awaitable Twilio notification tasks.

=====
Usage
=====

-----------------------
Notify one phone number
-----------------------

Use the :literal:`create_notification()` method on your :literal:`TwilioCaller` instance to create an asyncronous notification task::

    from caller import TwilioCaller

    caller = TwilioCaller()
    task = caller.create_notification(
        to_number="+15555555555",
        message="This is a test message.",
        method="sms",
    )
    
After you've created a task using :literal:`create_notification()`, execute it in asyncio's event runner::

    import asyncio

    asyncio.run(task)

-----------------------------
Notify multiple phone numbers
-----------------------------

Use the :literal:`create_tasks()` function with a list of phone numbers to create a list of awaitable tasks::

    from caller import TwilioCaller

    message: str = "This is a test message."
    phone_numbers: list[str] = [
        "+15555555555",
        "+17133049421",
        "+18324558034",
    ]
    caller = TwilioCaller()
    tasks = create_tasks(
        phone_numbers,
        message=message,
        method="sms",
        caller=caller
    )
    
After you've created a list of tasks using :literal:`create_tasks()`, execute the tasks using :literal:`asyncio.gather()`::

    import asyncio

    asyncio.gather(*tasks) # Use a '*' to unpack the list into asyncio.gather()
