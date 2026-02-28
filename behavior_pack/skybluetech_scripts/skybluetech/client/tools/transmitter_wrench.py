import time
from skybluetech_scripts.tooldelta.events.client import ClientBlockUseEvent

last_x = 0
last_y = 0
last_z = 0
last_click_time = 0


@ClientBlockUseEvent.Listen()
def onClientBlockUseEvent(event):
    # type: (ClientBlockUseEvent) -> None
    global last_x, last_y, last_z, last_click_time
    if event.blockName.startswith("skybluetech:") and (
        "cable" in event.blockName
        or "pipe" in event.blockName 
    ):
        nowtime = time.time()
        if last_x == event.x and last_y == event.y and last_z == event.z and nowtime - last_click_time < 0.1:
            event.cancel()
        last_x = event.x
        last_y = event.y
        last_z = event.z
        last_click_time = nowtime

