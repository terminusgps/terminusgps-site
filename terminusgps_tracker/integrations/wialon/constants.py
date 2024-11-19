import terminusgps_tracker.integrations.wialon.flags as flag

UNIT_GROUP_BASIC = sum(
    [
        flag.ACCESSFLAG_VIEW_ITEM_BASIC,
        flag.ACCESSFLAG_VIEW_ITEM_DETAILED,
        flag.ACCESSFLAG_RENAME_ITEM,
        flag.ACCESSFLAG_VIEW_CUSTOM_FIELDS,
        flag.ACCESSFLAG_MANAGE_CUSTOM_FIELDS,
        flag.ACCESSFLAG_MANAGE_ICON,
        flag.ACCESSFLAG_QUERY_REPORTS,
        flag.ACCESSFLAG_VIEW_ATTACHED_FILES,
        flag.ACCESSFLAG_UNIT_EXECUTE_COMMANDS,
        flag.ACCESSFLAG_UNIT_VIEW_SERVICE_INTERVALS,
        flag.ACCESSFLAG_UNIT_REGISTER_EVENTS,
        flag.ACCESSFLAG_UNIT_IMPORT_MESSAGES,
        flag.ACCESSFLAG_UNIT_EXPORT_MESSAGES,
    ]
)

UNIT_FULL_ACCESS_MASK = flag.ACCESSFLAG_FULL_ACCESS

WIALON_ITEM_TYPES: tuple = (
    "avl_hw",
    "avl_resource",
    "avl_retranslator",
    "avl_unit",
    "avl_unit_group",
    "user",
    "avl_route",
)

WIALON_ITEM_PROPERTIES: tuple = (
    "sys_name",
    "sys_id",
    "sys_unique_id",
    "sys_phone_number",
    "sys_phone_number2",
    "sys_user_creator",
    "rel_user_creator_name",
    "sys_billing_account_guid",
    "rel_billing_account_name",
    "rel_billing_parent_account_name",
    "rel_billing_plan_name",
    "sys_comm_state",
    "rel_hw_type_name",
    "rel_hw_type_id",
    "sys_account_balance",
    "sys_account_days",
    "sys_account_enable_parent",
    "sys_account_disabled",
    "rel_account_disabled_mod_time",
    "rel_account_units_usage",
    "rel_last_msg_date",
    "rel_is_account",
    "login_date",
    "retranslator_enabled",
    "rel_creation_time",
    "rel_group_unit_count",
    "rel_customfield_name",
    "rel_customfield_value",
    "profilefield",
    "rel_profilefield_name",
    "rel_profilefield_value",
    "rel_adminfield_name",
    "rel_adminfield_value",
    "rel_customfield_name_value",
    "rel_profilefield_name_value",
    "rel_adminfield_name_value",
)

WIALON_PROPERTY_TYPES: tuple = (
    "property",
    "list",
    "propitemname",
    "creatortree",
    "accounttree",
    "customfield",
    "profilefield",
    "adminfield",
)
