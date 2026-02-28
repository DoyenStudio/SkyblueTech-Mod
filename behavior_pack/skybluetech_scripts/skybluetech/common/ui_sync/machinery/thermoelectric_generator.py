# coding=utf-8

from skybluetech_scripts.tooldelta.extensions.ui_sync import S2CSync


class ThermoelectricGeneratorUISync(S2CSync):
    heat_val = 0
    cool_val = 0
    storage_rf = 0
    rf_max = 0
    power = 0

    def Unmarshal(self, data):
        self.heat_val = data["heat"]
        self.cool_val = data["cool"]
        self.storage_rf = data["rf"]
        self.rf_max = data["rf_max"]
        self.power = data["power"]

    def Marshal(self):
        return {
            "heat": self.heat_val,
            "cool": self.cool_val,
            "rf": self.storage_rf,
            "rf_max": self.rf_max,
            "power": self.power
        }
