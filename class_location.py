import config
from class_bin import BinID


class LocationBase:
    def __init__(self, bin_id: BinID):
        self.bin = bin_id

        config2 = config.LOCATION_CONFIG[self.bin.location]
        self.max_zone_alpha = config2["MAX_ZONE_ALPHA"]
        self.max_zone_num = {a: config2["MAX_ZONE_NUM"] for a in self.max_zone_alpha}

    def get_priority_order(self):
        raise NotImplementedError("Subclass must implement this method")

# =========================================================
# 3️⃣ Setup each Location
# =========================================================
class LocationA10(LocationBase):
    def get_priority_order(self):
        return ["A10", "A20", "A30"]


class LocationA20(LocationBase):
    def get_priority_order(self):
        # max_zone = self.MAX_ZONE_NUM.get(self.bin.zone_alpha, 0)
        max_zone = self.max_zone_num.get(self.bin.zone_alpha, 0)
        half_zone = round(max_zone / 2)
        if self.bin.zone_num <= half_zone:
            return ["A20", "A10", "A30"]
        else:
            return ["A20", "A30", "A10"]


class LocationA30(LocationBase):
    def get_priority_order(self):
        return ["A30", "A20", "A10"]


class LocationA40(LocationBase):
    def get_priority_order(self):
        return ["A40"]


class LocationA50(LocationBase):
    def get_priority_order(self):
        return ["A50"]