DANGEROUS = {
    "DELETE_FILE",
    "DELETE_FOLDER",
    "RUN_COMMAND",
    "SEND_EMAIL",
    "SET_REMINDER",
    "INSTALL_SOFTWARE",
}


def validate(actions):
    if not isinstance(actions, list):
        return {"requires_confirmation": False, "reason": ""}
    for action in actions:
        if not isinstance(action, dict):
            continue
        action_type = action.get("type")
        if action_type in DANGEROUS:
            return {
                "requires_confirmation": True,
                "reason": f"The action '{action_type}' requires user confirmation.",
            }
    return {"requires_confirmation": False, "reason": ""}
