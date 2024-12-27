Registration Flow
=================

1. ``GET /signup/``

2. ``POST /signup/``
   
    1. Create Django user
    2. Create TrackerProfile
    3. Create TrackerSubscription
    4. Create Wialon super user
    5. Create Wialon end user
    6. Create Wialon group
    7. Create Wialon resource

3. ``GET /profile/``

4. ``GET /profile/assets/new/``

5. ``POST /profile/assets/new/``

    1. Get unit ID via IMEI #
    2. Get unactivated Wialon unit group
    3. Get Wialon user via profile
    4. Get Wialon unit via ID
    5. Pop unit off unactivated group
    6. Rename Wialon unit
    7. Grant Wialon user access to Wialon unit
    8. Create TrackerAsset
    9. Set asset commands
    10. Save asset

6. ``GET /profile/``
