from ..core import CategoryType, RegisterDescription

content = "使用§2剪刀§r对草丛进行挖掘可得到矮草丛或高草丛。"

RegisterDescription(
    {CategoryType.ITEM: ["minecraft:short_grass", "minecraft:tall_grass"]},
    "草丛的获取方法",
    content.strip(),
)
