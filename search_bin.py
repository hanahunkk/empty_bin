import config
from search_zone import get_zone_number
# from bin_class import BinID, get_location_handler, LocationBase, LocationA10, LocationA20, LocationA30

# config.LOCATION_CONFIG = {
#     "A10": {"CATEGORY": "DRY", "MAX_ZONE_ALPHA":list("ABCDEFGHI"), "START_ZONE_NUM": 0, "MAX_ZONE_NUM": 33},
#     "A20": {"CATEGORY": "DRY", "MAX_ZONE_ALPHA":list("ABCDEFGHI"), "START_ZONE_NUM": 0, "MAX_ZONE_NUM": 45},
#     "A30": {"CATEGORY": "DRY", "MAX_ZONE_ALPHA":list("ABCDEFGHI"), "START_ZONE_NUM": 0, "MAX_ZONE_NUM": 23},
#     "A40": {"CATEGORY": "CHL", "MAX_ZONE_ALPHA":list("ABCDEFGHI"), "START_ZONE_NUM": 0, "MAX_ZONE_NUM": 70},
#     "A50": {"CATEGORY": "FRZ", "MAX_ZONE_ALPHA":list("ABCDEFGHI"), "START_ZONE_NUM": 0, "MAX_ZONE_NUM": 70},
# }

for loc, info in config.LOCATION_CONFIG.items():
    info["MID_ZONE_NUM"] = (info["MAX_ZONE_NUM"] + 1) // 2
# =========================================================
# 1️⃣ BinID
# =========================================================
class BinID:

    def __init__(self, code: str):
        self.bin_number = code.strip()
        # self.MAX_ZONE_ALPHA = None
        parts = code.split("-")
        self.location = parts[0] if len(parts) > 0 else None
        self.zone = parts[1] if len(parts) > 1 else None
        self.devan_height = parts[2] if len(parts) > 2 else None

        # zone (D08 → D + 08)
        if self.zone:
            self.zone_alpha = self.zone[0]           # 'D'
            try:
                self.zone_num = int(self.zone[1:])   # 8
            except ValueError:
                self.zone_num = None
        else:
            self.zone_alpha = None
            self.zone_num = None

        # max_zone_num and category
        info = config.LOCATION_CONFIG.get(self.location, {"CATEGORY": None,
                                                   "MAX_ZONE_ALPHA": list("ABCDEFGHI"),
                                                   "START_ZONE_NUM": 0,
                                                   "MAX_ZONE_NUM": 999,
                                                   "MID_ZONE_NUM": None},                                   )
        self.category = info["CATEGORY"]
        self.start_zone_num = info["START_ZONE_NUM"]
        self.max_zone_num = info["MAX_ZONE_NUM"]
        self.mid_zone_num = info["MID_ZONE_NUM"]
        self.max_zone_alpha = info["MAX_ZONE_ALPHA"]

        if self.zone_num is not None:
            if self.zone_num% 2 == 0:
                self.max_zone_num -= 1

        # zone
        if self.zone:
            self.zone_alpha = self.zone[0]
            try:
                self.zone_num = int(self.zone[1:])
                self.zone_num = min(self.zone_num, self.max_zone_num)
            except ValueError:
                self.zone_num = None
        else:
            self.zone_alpha = None
            self.zone_num = None

    def _replace(self, **kwargs):
        location = kwargs.get("location", self.location)
        zone_alpha = kwargs.get("zone_alpha", self.zone_alpha)
        zone_num = kwargs.get("zone_num", self.zone_num)
        devan_height = kwargs.get("devan_height", self.devan_height)
        return BinID(f"{location}-{zone_alpha}{zone_num:02d}-{devan_height}")

    @property
    def is_even(self) -> bool:
        return self.zone_num % 2 == 0

    @property
    def is_odd(self) -> bool:
        return self.zone_num % 2 != 0

    def __repr__(self):
        parity = "even" if self.is_even else "odd"
        return (f"<BinID {self.bin_number} "
                f"(loc={self.location}, zone={self.zone_alpha}{self.zone_num:02d}, "
                f"h={self.devan_height}, {parity}, {self.bin_number})>")

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
        return "type1", ["A10", "A20", "A30"]

class LocationA20(LocationBase):
    def get_priority_order(self):
        # max_zone = self.MAX_ZONE_NUM.get(self.bin.zone_alpha, 0)
        max_zone = self.max_zone_num.get(self.bin.zone_alpha, 0)
        half_zone = round(max_zone / 2)
        if self.bin.zone_num <= half_zone:
            return "type2", ["A20", "A10", "A30"]
        else:
            return "type2", ["A20", "A30", "A10"]

class LocationA30(LocationBase):
    def get_priority_order(self):
        return "type3", ["A30", "A20", "A10"]


class LocationA40(LocationBase):
    def get_priority_order(self):
        return ["A40"]

class LocationA50(LocationBase):
    def get_priority_order(self):
        return ["A50"]

# =========================================================
# 4️⃣ Factory function
# =========================================================
def get_location_handler(bin_id: BinID) -> LocationBase:
    mapping = {
        "A10": LocationA10,
        "A20": LocationA20,
        "A30": LocationA30,
        "A40": LocationA40,
        "A50": LocationA50,
    }
    handler_class = mapping.get(bin_id.location, LocationBase)
    return handler_class(bin_id)


def location_A10(input_record, criteria_id, df_empty_bins, search_times):
    count_empty = get_zone_number(input_record, criteria_id, df_empty_bins, search_times)
    return count_empty


def location_A20(input_record, criteria_id, df_empty_bins, search_times):
    count_empty = get_zone_number(input_record, criteria_id, df_empty_bins, search_times)
    return count_empty


def location_A30(input_record, criteria_id,df_empty_bins, search_times):
    count_empty = get_zone_number(input_record, criteria_id, df_empty_bins, search_times)
    return count_empty


def location_A40(input_record, criteria_id,df_empty_bins, bin_origin):
    return 0


def location_A50(input_record, criteria_id,df_empty_bins, bin_origin):
    return 0


def search_bin(input_record, df_empty_bins, search_times) -> None:
    input_bin = str(input_record.get('Preferred Bin'))
    # print(f"type of input_bin ({type(input_bin)})")
    bin = BinID(input_bin)

    handler = get_location_handler(bin)
    location_type, location_order = handler.get_priority_order()
    print(f"input_bin : {input_bin}, bin : {bin} , location_type : {location_type} , location_order: {location_order}")

    total_count = 0
    check_flag = 0
    # found = False
    for loc in location_order:
        func = globals().get(f"location_{loc}")

        if not func:
            continue

        if check_flag == 1:
            if location_type == "type1":
                start_num = config.LOCATION_CONFIG[loc]["START_ZONE_NUM"]
            elif location_type == "type2":
                if loc == "A10":
                    start_num = config.LOCATION_CONFIG[loc]["MAX_ZONE_NUM"]
                else:  # loc == "A30"
                    start_num = config.LOCATION_CONFIG[loc]["START_ZONE_NUM"]
            else:  # type3
                start_num = config.LOCATION_CONFIG[loc]["MAX_ZONE_NUM"]

            next_location_bin = \
                (f"{loc}-"
                 f"{bin.zone_alpha}{start_num:02d}-"
                 f"01")
            bin = BinID(next_location_bin)
            print(f"next_location_bin {bin} ")


        count_empty = func(input_record, bin, df_empty_bins, search_times)
        total_count += count_empty

        if total_count > 0:
            break
        else:
            print(f"⚠️ Weight Not enough loc({loc}) {total_count}")
            check_flag = 1
            continue


if __name__ == "__main__":
    search_bin()