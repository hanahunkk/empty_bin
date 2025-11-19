import pandas as pd
import re, os
import config


class StockList:
    """
    Read the Recent ItemStockList.xlsx, AKL worksheet
    Get column Item Code / Standard
    """

    def __init__(self, source_dir: str = config.STOCKLIST_DIR):
        self.source_dir = source_dir
        self.file_path = self._find_latest_stocklist()
        self.df = None

        if self.file_path:
            self._load_data()
        else:
            print("⚠️ No ItemStockList file found.")

    def _find_latest_stocklist(self) -> str | None:
        pattern = re.compile(r"(\d+)-ItemStockList\.xlsx$")
        max_num = -1
        latest_file = None

        for file in os.listdir(self.source_dir):
            match = pattern.match(file)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
                    latest_file = os.path.join(self.source_dir, file)

        return latest_file

    def _load_data(self):
        try:
            df_all = pd.read_excel(self.file_path, sheet_name="AKL")

            if {"ITEM CODE", "STANDARD"}.issubset(df_all.columns):
                df = df_all[["ITEM CODE", "STANDARD"]].copy()

                # Remove Space
                df["ITEM CODE"] = df["ITEM CODE"].astype(str).str.strip()

                # Unique
                before = len(df)
                df = df.drop_duplicates(subset=["ITEM CODE"], keep="first").reset_index(drop=True)
                after = len(df)

                print(f"📊 Loaded {after} unique Item Codes (removed {before - after} duplicates)")
                self.df = df
            else:
                print("⚠️ No 'Item Code' or 'Standard' Column")
        except Exception as e:
            print(f"❌ Read Error Excel: {e}")

    def get(self) -> pd.DataFrame | None:
        return self.df

    def __call__(self) -> pd.DataFrame | None:
        return self.df


    @classmethod
    def item_standard(cls) -> pd.DataFrame:

        stock = cls()

        if stock.df is None:
            raise RuntimeError("❌ StockList Failed to load data.")

        df = stock.df.copy()

        # 1. Split with '/'
        df[["front", "back"]] = df["STANDARD"].str.split("/", n=1, expand=True)

        # ② Split between number and letter
        df["num"] = df["front"].str.extract(r"(\d+(?:\.\d+)?)")   # number
        df["unit"] = df["front"].str.extract(r"([a-zA-Z]+)")      # letter

        # ③ change num to numeric
        df["num"] = pd.to_numeric(df["num"], errors="coerce")

        # ④ Filtering
        cond_num = df["num"] >= config.HEAVY_NUM
        cond_unit = df["unit"].str.lower().isin(config.ITEM_STANDARD_UNIT)
        cond_code = df["ITEM CODE"].str.upper().str.startswith(config.TFC_CODE_PREFIX_FOOD)

        df["heavy_flag"] = ((cond_num) & (cond_unit) & (cond_code)).astype(int)

        return df
