# coding=utf-8
from ..internal import ServerComp, ServerLevelId, ClientComp, ClientLevelId, InServerEnv, InClientEnv

itemBasicInfoPool = {} # type: dict[str, BasicItemInfo]

class Item(object):
    newItemName = '' # type: str
    """必须设置，物品的identifier，即"命名空间:物品名" """
    newAuxValue = 0 # type: int
    """必须设置，物品附加值"""
    itemName = '' # type: str
    """（废弃）1.22及以前版本的旧identifier，详见1.23版本物品id变更"""
    auxValue = 0 # type: int
    """（废弃）1.22及以前版本的旧物品附加值，详见1.23版本物品id变更"""
    count = 0 # type: int
    """必须设置，物品数量。设置为0时为空物品"""
    showInHand = False # type: bool
    """可选，是否显示在手上，默认为True"""
    enchantData = None # type: list[tuple[int, int]] | None
    """可选，附魔数据，tuple中 EnchantType 为附魔类型，int为附魔等级"""
    modEnchantData = None # type: list[tuple[str, int]] | None
    """可选，自定义附魔数据，tuple中str为自定义附魔id，int为自定义附魔等级"""
    customTips = None # type: str | None
    """可选，物品的自定义tips，修改该内容后会覆盖实例的组件netease:customtips的内容"""
    extraId = None # type: str | None
    """可选，物品自定义标识符。可以用于保存数据， 区分物品"""
    userData = None # type: dict | None
    """可选，物品userData，用于灾厄旗帜、旗帜等物品，请勿随意设置该值"""
    durability = 0 # type: int
    """可选，物品耐久度，不存在耐久概念的物品默认值为零"""

    def __init__(
        self,
        newItemName, # type: str
        newAuxValue=0, # type: int
        count=1, # type: int
        showInHand=True, # type: bool
        enchantData=None, # type: list[tuple[int, int]] | None
        modEnchantData=None, # type: list[tuple[str, int]] | None
        customTips="", # type: str | None
        extraId=None, # type: str | None
        userData=None, # type: dict | None
        durability=0, # type: int
        _orig=None # type: dict | None
    ):
        # type: (...) -> None
        self.newItemName = newItemName
        self.newAuxValue = newAuxValue
        self.itemName = newItemName
        self.auxValue = newAuxValue
        self.count = count
        self.showInHand = showInHand
        self.enchantData = enchantData
        self.modEnchantData = modEnchantData
        self.customTips = customTips
        self.extraId = extraId
        self.userData = userData
        self.durability = durability
        self._orig = _orig or {}

    @classmethod
    def from_dict(cls, data):
        # type: (dict) -> Item
        return cls(
            data["newItemName"],
            data["newAuxValue"],
            data["count"],
            data["showInHand"],
            data.get("enchantData"),
            data.get("modEnchantData"),
            data.get("customTips"),
            data.get("extraId"),
            data.get("userData"),
            data.get("durability", 0),
            _orig = data,
        )

    def unmarshal(self, data):
        # type: (dict) -> None
        self._orig = data
        self.newItemName = data["newItemName"]
        self.newAuxValue = data["newAuxValue"]
        self.itemName = data["itemName"]
        self.auxValue = data["auxValue"]
        self.count = data["count"]
        self.showInHand = data["showInHand"]
        self.enchantData = data.get("enchantData")
        self.modEnchantData = data.get("modEnchantData")
        self.customTips = data.get("customTips")
        self.extraId = data.get("extraId")
        self.userData = data.get("userData")
        self.durability = data.get("durability", 0)

    def marshal(self):
        # type: () -> dict
        ret = self._orig.copy()
        ret.update({
            "newItemName": self.newItemName,
            "newAuxValue": self.newAuxValue,
            "itemName": self.itemName,
            "auxValue": self.auxValue,
            "count": self.count,
            "showInHand": self.showInHand,
            "enchantData": self.enchantData,
            "modEnchantData": self.modEnchantData,
        }) # type: dict
        if self.enchantData is not None:
            ret["enchantData"] = self.enchantData
        if self.modEnchantData is not None:
            ret["modEnchantData"] = self.modEnchantData
        if self.customTips is not None:
            ret["customTips"] = self.customTips
        if self.extraId is not None:
            ret["extraId"] = self.extraId
        if self.userData is not None:
            ret["userData"] = self.userData
        if self.durability is not None:
            ret["durability"] = self.durability
        return ret

    def ApplyModifies(self):
        """ 将修改应用于物品指向的 itemDict。 """
        self._orig.update(self.marshal())

    @property
    def id(self):
        return self.newItemName

    @property
    def isEnchanted(self):
        return bool(self.enchantData or self.modEnchantData)

    def GetBasicInfo(self):
        cached = itemBasicInfoPool.get(self.newItemName)
        if cached is not None:
            return cached
        if InServerEnv():
            raw_info = ServerComp.CreateItem(ServerLevelId).GetItemBasicInfo(
                self.newItemName, self.newAuxValue, self.isEnchanted
            )
            if raw_info is None:
                raise ValueError("Can't get basic info of " + self.newItemName)
            res = BasicItemInfo().unmarshal(raw_info)
        else:
            res = BasicItemInfo().unmarshal(
                ClientComp.CreateItem(ClientLevelId).GetItemBasicInfo(
                    self.newItemName, self.newAuxValue, self.isEnchanted
                )
            )
        itemBasicInfoPool[self.newItemName] = res
        return res

    def CanMerge(self, other, deny_enchant=True):
        # type: (Item, bool) -> bool
        if self.durability != 0:
            return False
        elif deny_enchant and (self.enchantData or self.modEnchantData):
            return False
        return (
            self.newItemName == other.newItemName
            and self.newAuxValue == other.newAuxValue
            and (self.enchantData == other.enchantData or (not self.enchantData and not other.enchantData))
            and (self.modEnchantData == other.modEnchantData or (not self.modEnchantData and not other.modEnchantData))
            and self.userData == other.userData
            and self.durability == other.durability
        )

    def StackFull(self):
        return self.count >= self.GetBasicInfo().maxStackSize

    def modifyCustomTips(self, tips):
        # type: (str) -> None
        self.customTips = tips
        self._orig["customTips"] = tips

    def SetDurability(self, durability):
        # type: (int) -> None
        self.durability = durability
        self._orig["durability"] = durability

    def copy(self):
        return Item(
            self.newItemName,
            self.newAuxValue,
            self.count,
            self.showInHand,
            self.enchantData.copy() if self.enchantData else None,
            self.modEnchantData.copy() if self.modEnchantData else None,
            self.customTips,
            self.extraId,
            self.userData.copy() if self.userData else None,
            self.durability,
            _orig = self._orig.copy(),
        )


class BasicItemInfo(object):
    itemName = '' # type: str
    """ 本地化的物品名字 """
    maxStackSize = 0 # type: int
    """ 物品最大堆叠数目 """
    maxDurability = 0 # type: int
    """ 物品最大耐久值 """
    id_aux = 0 # type: int
    """ 主要用于客户端的ui绑定，详见客户端接口 """
    tierDict = {} # type: dict
    """ 自定义方块定义的挖掘相关的属性 netease:tier,没有设置时返回None """
    itemCategory = '' # type: str
    """ 创造栏分类 """
    itemType = '' # type: str
    """ 物品类型 """
    customItemType = '' # type: str
    """ 自定义物品类型 """
    tags = set() # type: set[str]
    """ 物品的tags列表，如['minecraft:is_food'] """
    customTips = '' # type: str
    """ 自定义物品/方块tips """
    itemTierLevel = 0 # type: int
    """ 工具等级 """
    fuelDuration = 0.0 # type: float
    """ 燃料时长 """
    foodNutrition = 0 # type: int
    """ 食物营养值 """
    foodSaturation = 0.0 # type: float
    """ 食物饱食度 """
    weaponDamage = 0 # type: int
    """ 武器攻击力 """
    armorDefense = 0 # type: int
    """ 防具防御力 """
    armorSlot = 0 # type: int
    """ 防具槽位 """
    armorToughness = 0 # type: int
    """ 防具韧性 """
    armorKnockbackResistance = 0.0 # type: float
    """ 防具击退抗性 """
    enchant_slot_type = 0 # type: int
    """ 附魔槽位枚举标志 自定义附魔文档 """


    def unmarshal(self, data):
        self.itemName = data["itemName"]
        self.maxStackSize = data["maxStackSize"]
        self.maxDurability = data["maxDurability"]
        self.id_aux = data["id_aux"]
        self.tierDict = data["tierDict"]
        self.itemCategory = data["itemCategory"]
        self.itemType = data["itemType"]
        self.customItemType = data["customItemType"]
        self.tags = set(data["tags"])
        self.customTips = data["customTips"]
        self.itemTierLevel = data["itemTierLevel"]
        self.fuelDuration = data["fuelDuration"]
        self.foodNutrition = data["foodNutrition"]
        self.foodSaturation = data["foodSaturation"]
        self.weaponDamage = data["weaponDamage"]
        self.armorDefense = data["armorDefense"]
        self.armorSlot = data["armorSlot"]
        self.armorToughness = data["armorToughness"]
        self.armorKnockbackResistance = data["armorKnockbackResistance"]
        self.enchant_slot_type = data["enchant_slot_type"]
        return self

    def marshal(self):
        # type: () -> dict
        return {
            "itemName": self.itemName,
            "maxStackSize": self.maxStackSize,
            "maxDurability": self.maxDurability,
            "id_aux": self.id_aux,
            "tierDict": self.tierDict,
            "itemCategory": self.itemCategory,
            "itemType": self.itemType,
            "customItemType": self.customItemType,
            "tags": list(self.tags),
            "customTips": self.customTips,
            "itemTierLevel": self.itemTierLevel,
            "fuelDuration": self.fuelDuration,
            "foodNutrition": self.foodNutrition,
            "foodSaturation": self.foodSaturation,
            "weaponDamage": self.weaponDamage,
            "armorDefense": self.armorDefense,
            "armorSlot": self.armorSlot,
            "armorToughness": self.armorToughness,
            "armorKnockbackResistance": self.armorKnockbackResistance,
            "enchant_slot_type": self.enchant_slot_type,
        }

__all__ = [
    "Item",
    "BasicItemInfo",
    "itemBasicInfoPool",
]