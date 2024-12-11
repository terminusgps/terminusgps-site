Settings
========

Before using :literal:`terminusgps-notifier`, ensure you have the following values set in your project's environment:

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
