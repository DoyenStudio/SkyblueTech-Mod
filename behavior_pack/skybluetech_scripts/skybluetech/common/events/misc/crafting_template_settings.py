# coding=utf-8
from skybluetech_scripts.tooldelta.events.basic import CustomS2CEvent, CustomC2SEvent


class CraftingTemplateSettingsUpload(CustomC2SEvent):
    name = "st:CTSU"

    def __init__(self, template_slotitems, player_id=""):
        # type: (list[tuple[str, int] | None], str) -> None
        self.template_slotitems = template_slotitems
        self.player_id = player_id

    def marshal(self):
        return {"s": self.template_slotitems}

    @classmethod
    def unmarshal(cls, data):
        return cls(
            template_slotitems=data["s"],
            player_id=data["__id__"]
        )


class CraftingTemplateUpdateRecipe(CustomS2CEvent):
    name = "st:CTUOS"

    def __init__(self, recipe_data):
        # type: (dict | None) -> None
        self.recipe_data = recipe_data

    def marshal(self):
        return self.recipe_data

    @classmethod
    def unmarshal(cls, data):
        return cls(recipe_data=data)
