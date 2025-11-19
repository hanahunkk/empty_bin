import config

for loc, info in config.LOCATION_CONFIG.items():
    info["MID_ZONE_NUM"] = (info["MAX_ZONE_NUM"] + 1) // 2


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
                                                   "MID_ZONE_NUM": None},
                                          )
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

