# coding=utf-8
from skybluetech_scripts.skybluetech.common.define import id_enum
from skybluetech_scripts.skybluetech.client.ui.recipe_checker import (
    CheckRecipe,
    CheckUsage,
)
from ...define import (
    TextPage,
    PageGroup,
)

resin_collect = PageGroup(
    "resin_collect",
    [
        TextPage(
            "树脂人工采集",
            '你可以将<item id="{resin_collector}"><link id="resin_collector" text="树脂采集斗">放到小棵橡树的树干上收集<item id="{resin}">生树脂。 生树脂可以经熔炉烧制成<item id="{rough_rubber}"><link id="rough_rubber" text="粗橡胶">。\n\n<text color="§c" t="注意， 光秃秃的橡树是没办法产出树脂的； 所以不要试图在树叶全剪掉的橡树上采集树脂。">'.format(
                resin_collector=id_enum.RESIN_COLLECTOR,
                resin=id_enum.RESIN,
                rough_rubber=id_enum.ROUGH_RUBBER,
            ),
            hyperlink_cbs={
                "resin_collector": lambda _: CheckRecipe(id_enum.RESIN_COLLECTOR),
                "rough_rubber": lambda _: CheckUsage(id_enum.ROUGH_RUBBER),
            },
        ),
        TextPage(
            "",
            '用<item id="{resin_spoon}"><link id="resin_spoon" text="树脂采集勺">点击盛有生树脂的树脂采集斗以<text color="§a" t="收集树脂">。'.format(
                resin_spoon=id_enum.RESIN_SPOON
            ),
            hyperlink_cbs={
                "resin_spoon": lambda _: CheckRecipe(id_enum.RESIN_SPOON),
            },
        ),
        TextPage(
            "液态树脂自动化采集",
            '将<item id="{outputer}"><link id="outputer" text="树脂导流斗">放在树脂采集斗前方， 新生成的每份生树脂会优先转为 <text color="§6" t="244 mB 液态生树脂">，与熔化仓的转化量相同。 输出斗可储存至多<text color="§2" t="1000 mB">液态生树脂， 可以被流体管道抽取。 '.format(
                outputer=id_enum.Machinery.RESIN_COLLECTOR_OUTPUTER,
            ),
            hyperlink_cbs={
                "outputer": lambda _: CheckRecipe(
                    id_enum.Machinery.RESIN_COLLECTOR_OUTPUTER
                )
            },
        ),
        TextPage(
            "",
            '容量不足以容纳下一份时，树脂会溢出并<text color="§c" t="硬化">， 无法再被自动导流进管道。这时候只能手动用树脂采集勺将硬化树脂<text color="§c" t="全部舀完">后， 新生成的树脂才能继续被自动导流到管道内。',
        ),
    ],
)
