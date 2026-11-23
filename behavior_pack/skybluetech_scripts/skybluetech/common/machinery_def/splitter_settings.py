# coding=utf-8
K_RECORD_LABELS = "record_settings"
K_SETTINGS_LIMIT = "settings_limit"

ITEM_SPLITTER_DEFAULT_ITEM = "minecraft:iron_ingot"
ITEM_SPLITTER_SETTINGS_LIMIT = 6
FLUID_SPLITTER_DEFAULT_FLUID = "minecraft:water"
FLUID_SPLITTER_SETTINGS_LIMIT = 3


def LoadSplitterSettings(records, default_id):
    # type: (list[str] | None, str) -> list[tuple[int, str]]
    if records is None:
        return [(0, default_id)]
    settings = []
    for record in records:
        label, content_id = record.split("-", 1)
        settings.append((int(label), str(content_id)))
    return settings


def SaveSplitterSettings(settings):
    # type: (list[tuple[int, str]]) -> list[str]
    return ["%d-%s" % (label, content_id) for label, content_id in settings]
