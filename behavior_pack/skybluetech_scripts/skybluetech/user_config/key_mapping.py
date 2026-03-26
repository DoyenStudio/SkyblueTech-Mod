# coding=utf-8
from skybluetech_scripts.tooldelta.extensions.ctrl_settings import Control as C

MOD_NAME = "蔚蓝科技"


RF_REPEATER_BUILD_CANCEL = C(
    MOD_NAME, "能源中继器-取消布线", C.KEY().KEY_O, C.GAMEPAD().UNDEFINED
)
RF_REPEATER_BUILD_CONFIRM = C(
    MOD_NAME, "能源中继器-确认布线", C.KEY().KEY_F, C.GAMEPAD().UNDEFINED
)
