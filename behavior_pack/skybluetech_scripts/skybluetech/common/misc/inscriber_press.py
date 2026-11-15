# coding=utf-8
EMPTY = "skybluetech:inscriber_press_empty"
STICK = "skybluetech:inscriber_press_stick"
GRID_KEY = "skybluetech:inscriber_press_grid"
IDENTITY_KEY = "skybluetech:inscriber_press_identity"
SCREEN = "InscriberPressEditorUI.main"
HOLD_SECONDS = 0.6
STICK_GRID = [0 if row + col == 7 else 1 for row in range(8) for col in range(8)]


def ReadGrid(user_data):
    raw = (user_data or {}).get(GRID_KEY)
    if raw is None:
        return [1] * 64
    if not isinstance(raw, list) or len(raw) != 64:
        return None
    result = []
    for entry in raw:
        if not isinstance(entry, dict) or entry.get("__type__") != 3:
            return None
        value = entry.get("__value__")
        if type(value) is not int or value not in (0, 1):
            return None
        result.append(value)
    return result
