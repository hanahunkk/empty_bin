# main.py / class_empty_bin.py
EMPTYBIN_DIR = r"\\Tfc-akl-share\tfc共有\物流部\物流部\EmptyBin"

# process_file.py / search_zone
REF_LIST = []

# class_empty_bin.py
BASE_INPUT_FILE = "bins.csv"
BASE_INPUT_FILE_FLAG = 0    # 0 : bins.csv
                            # 1 : others
INPUT_FILE_NAME = ""


# class_stocklist.py
STOCKLIST_DIR = r"\\Tfc-akl-share\tfc共有\物流部\物流部\ItemStockSearch"
HEAVY_NUM = 18  # Based on Standard weight kg or l
TFC_CODE_PREFIX_FOOD = ("A", "B", "D", "E")
ITEM_STANDARD_UNIT = ["kg", "l"]


# search_zone.py
MAX_EMPTY_BINS = 1
PHASE_MAX = 40
MAX_HEIGHT = 15
MAX_HEIGHT_HEAVY = 6


# search_bin.py
LOCATION_CONFIG = {
    "A10": {"CATEGORY": "DRY", "MAX_ZONE_ALPHA":list("ABCDEFGHI"), "START_ZONE_NUM": 0, "MAX_ZONE_NUM": 33},
    "A20": {"CATEGORY": "DRY", "MAX_ZONE_ALPHA":list("ABCDEFGHI"), "START_ZONE_NUM": 0, "MAX_ZONE_NUM": 45},
    "A30": {"CATEGORY": "DRY", "MAX_ZONE_ALPHA":list("ABCDEFGHI"), "START_ZONE_NUM": 0, "MAX_ZONE_NUM": 23},
    "A40": {"CATEGORY": "CHL", "MAX_ZONE_ALPHA":list("ABCDEFGHI"), "START_ZONE_NUM": 0, "MAX_ZONE_NUM": 70},
    "A50": {"CATEGORY": "FRZ", "MAX_ZONE_ALPHA":list("ABCDEFGHI"), "START_ZONE_NUM": 0, "MAX_ZONE_NUM": 70},
}
