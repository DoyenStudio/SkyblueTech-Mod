# class PowerData:
#     def __init__(self, store_rf, store_rf_total):
#         # type: (int, int) -> None
#         self.store_rf = store_rf
#         self.store_rf_total = store_rf_total

#     @classmethod
#     def from_data(cls, data, force=False):
#         # type: (BlockEntityData, bool) -> Optional[PowerData]
#         if not force:
#             if data["store_rf_total"] is None:
#                 return None
#         store_rf = data["store_rf"] or 0
#         store_rf_total = data["store_rf_total"] or 0
#         return PowerData(store_rf, store_rf_total)

#     @classmethod
#     def from_data_forced(cls, data):
#         # type: (BlockEntityData) -> PowerData
#         store_rf = data["store_rf"] or 0
#         store_rf_total = data["store_rf_total"] or 0
#         return PowerData(store_rf, store_rf_total)

#     def dumps(self, orig_data):
#         # type: (BlockEntityData) -> None
#         orig_data["store_rf"] = self.store_rf
#         orig_data["store_rf_total"] = self.store_rf_total


# def GetPowerData(data):
#     # type: (BlockEntityData) -> PowerData | None
#     return PowerData.from_data(data)


# def ForceGetPowerData(data):
#     # type: (BlockEntityData) -> PowerData
#     return PowerData.from_data_forced(data)

INFINITY = float("inf")

def FormatRF(rf):
    # type: (float) -> str
    suffixes = ("", "k", "M", "G", "T", "P", "E", "Z", "Y")
    d = 0
    if rf == INFINITY:
        return "无限 RF"
    while d < len(suffixes) and rf >= 1000:
        d += 1
        rf /= 1000.0
    return "%.2f %sRF" % (rf, suffixes[d])

def FormatFluidVolume(vol):
    # type: (float) -> str
    if vol == INFINITY:
        return "无限"
    elif vol >= 10000:
        return "%.2f B" % (float(vol) / 1000)
    else:
        return "%.0f mB" % vol

def FormatKelvin(k):
    # type: (float) -> str
    if k == INFINITY:
        return "Inf"
    suffixes = ("", "k", "M", "G", "T", "P", "E", "Z", "Y")
    d = 0
    while d < len(suffixes) and k >= 1000:
        d += 1
        k /= 1000.0
    return "%.2f %sK" % (k, suffixes[d])
