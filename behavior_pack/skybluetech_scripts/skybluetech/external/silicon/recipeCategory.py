# coding=utf-8
class RecipeCategory(object):

    def onLoaded(self):
        """
        当Silicon主界面被玩家打开时调用一次。
        """

    def getName(self):
        """
        获取标签页的唯一标识符，用于区分不同的标签页。
        支持小写字母、数字、下划线、冒号，其它字符可能会有未知问题。
        :rtype: str
        """
        return ''

    def getIcon(self):
        """
        获取标签页的图标，支持物品和图片，请使用方形的图片。
        物品格式 ('minecraft:apple', 0)
        图片格式 'textures/items/apple'
        :rtype: str|(str, int)
        """
        return ''

    def getSize(self):
        """
        获取标签页的横向大小和纵向大小。
        大小不建议超过162*162，不可超过200*200。
        :rtype: (int, int)
        """
        return 0, 0

    def getBackground(self):
        """
        获取标签页的背景图片。
        :rtype: str
        """
        return ''

    def getSlotControls(self):
        """
        获取标签页的物品控件。
        :rtype: dict[str, dict]
        """
        return {}

    def getOtherControls(self):
        """
        获取标签页的其它控件。
        :rtype: dict[str, dict]
        """
        return {}

    def checkAsInput(self, identifier, auxValue, userData):
        """
        将物品作为输入物品进行查询，需要返回查询到的数量。
        在查询后，Silicon会调用getCheckedRecipe方法进行显示，请将查询到的信息缓存到实例中，以便后续显示配方。
        :type identifier: str
        :type auxValue: int
        :type userData: dict
        :rtype: int
        """
        return 0

    def checkAsOutput(self, identifier, auxValue, userData):
        """
        将物品作为输出物品进行查询，需要返回查询到的数量。
        在查询后，Silicon会调用getCheckedRecipe方法进行显示，请将查询到的信息缓存到实例中，以便后续显示配方。
        :type identifier: str
        :type auxValue: int
        :type userData: dict
        :rtype: int
        """
        return 0

    def checkAllRecipes(self):
        """
        查询全部配方，需要返回查询到的数量。
        在查询后，Silicon会调用getCheckedRecipe方法进行显示，请将查询到的信息缓存到实例中，以便后续显示配方。
        :rtype: int
        """
        return 0

    def getCheckedRecipe(self, index):
        """
        根据索引获取查询到的配方。
        :type index: int
        :rtype: dict[str, dict|bool]
        """
        return {
            'slot': {},
            'other': {},
            'shapeless': False,
        }
