Glossary
========

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
