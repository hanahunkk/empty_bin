import os, re
import pandas as pd
import glob

STOCKLIST_DIR = r"\\Tfc-akl-share\tfc共有\物流部\物流部\ItemStockSearch"

class StockList:
    """
    Read the Recent ItemStockList.xlsx, AKL worksheet
    Get column Item Code / Standard
    """

    def __init__(self, source_dir: str = STOCKLIST_DIR):
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


class POFile:
    def __init__(self, path: str):
        self.path = path
        self.name = os.path.basename(path)
        self.sheet_names = []
        self.df_raw = None
        self.header_row_index = None
        self.df_clean = None


    def load(self) -> bool:
        try:
            with pd.ExcelFile(self.path) as xls:
                self.sheet_names = [s.lower() for s in xls.sheet_names]
            return True
        except Exception as e:
            print(f"❌ {self.name} → Excel load error: {e}")
            return False

    def has_sheet(self, sheet_name: str) -> bool:
        return sheet_name.lower() in self.sheet_names

    def read_sheet(self, sheet_name: str = "格納") -> bool:
        if not self.has_sheet(sheet_name):
            print(f"⚠️ {self.name} → '{sheet_name}' no sheet")
            return False
        try:
            self.df_raw = pd.read_excel(self.path, sheet_name=sheet_name, header=None)
            return True
        except Exception as e:
            print(f"❌ {self.name} → Sheet read error: {e}")
            return False

    def find_header_row(self, target_cols=None) -> int | None:
        if self.df_raw is None:
            print(f"⚠️ {self.name} → Data not loaded yet.")
            return None

        if target_cols is None:
            target_cols = ["Palllet#", "Tfc Code", "Preferred Bin", "格納先", "Memo", "Qt"]

        for i, row in self.df_raw.iterrows():
            row_values = row.astype(str).str.strip().tolist()
            match_count = sum(any(tc.lower() in str(val).lower() for val in row_values) for tc in target_cols)
            if match_count >= 3:
                self.header_row_index = i
                return i

        print(f"⚠️ {self.name} → header not found.")
        return None

    def extract_data(self):
        if self.header_row_index is None:
            self.find_header_row()

        if self.header_row_index is None:
            print(f"⚠️ {self.name} → header_row_index not set.")
            return None

        # Create head of df
        header = self.df_raw.iloc[self.header_row_index].tolist()
        df_data = self.df_raw.iloc[self.header_row_index + 1:].copy()
        df_data.columns = header

        # Remove completely empty rows
        df_data = df_data.dropna(how="all")

        # Select columns assigned
        keep_cols = ["Palllet#", "Tfc Code", "Preferred Bin", "格納先", "Memo", "Qt"]
        existing_cols = [c for c in keep_cols if c in df_data.columns]
        self.df_clean = df_data[existing_cols].reset_index(drop=True)

        self.df_clean["target_bin1"] = ""
        self.df_clean["target_bin2"] = ""
        self.df_clean["PO name"] = self.name

        return self.df_clean

    def __repr__(self):
        return f"POFile(name='{self.name}')"


class EmptyBin:

    def __init__(self, csv_path="bins.csv"):
        self.csv_path = csv_path
        self.df = None

    def load(self) -> bool:
        if not os.path.exists(self.csv_path):
            print(f"❌ File not found: {self.csv_path}")
            return False
        try:
            self.df = pd.read_csv(
                self.csv_path,
                header=0,
                usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                # encoding="utf-8-sig"
            )
            self.df.columns = [
                "No", "bin_number", "empty_flag", "criteria_id", "Palllet#",
                "Tfc Code", "Preferred Bin", "Memo", "Qt", "Target Bin1",
                "Target Bin2", "Target Bin3", "PO name"
            ]

            self.df["empty_flag"] = self.df["empty_flag"].fillna(0).astype(int)
            self.df["Palllet#"] = self.df["Palllet#"].fillna("").astype(str)
            self.df["Tfc Code"] = self.df["Tfc Code"].fillna("").astype(str)
            self.df["Preferred Bin"] = self.df["Preferred Bin"].fillna("").astype(str)
            self.df["Memo"] = self.df["Memo"].fillna("").astype(str)
            self.df["Qt"] = self.df["Qt"].fillna(0).astype(int)
            self.df["Target Bin1"] = self.df["Target Bin1"].fillna("").astype(str)
            self.df["Target Bin2"] = self.df["Target Bin2"].fillna("").astype(str)
            self.df["Target Bin3"] = self.df["Target Bin3"].fillna("").astype(str)
            self.df["PO name"] = self.df["PO name"].fillna("").astype(str)

            print(f"✅ Loaded {len(self.df)} rows from {os.path.basename(self.csv_path)}")
            return True

        except Exception as e:
            print(f"❌ Failed to load {self.csv_path}: {e}")
            return False

    # ---------------------------------------------------
    # 🔸 기능 메서드들
    # ---------------------------------------------------

    def get_by_criteria(self, criteria_id: str):
        """특정 criteria_id로 필터링"""
        if self.df is None:
            print("⚠️ Data not loaded.")
            return None
        result = self.df[self.df["criteria_id"] == criteria_id]
        return result

    def get_unique_preferred_bins(self):
        """Preferred Bin 컬럼의 고유값 리스트 반환"""
        if self.df is None:
            print("⚠️ Data not loaded.")
            return []
        return sorted(self.df["preferred_bin"].dropna().unique().tolist())

    def count_empty_bins(self):
        """empty_flag == 1 인 bin 개수"""
        if self.df is None:
            print("⚠️ Data not loaded.")
            return 0
        return int((self.df["empty_flag"] == 1).sum())

    def save(self, out_path=None):
        """수정된 df를 다시 CSV로 저장"""
        if self.df is None:
            print("⚠️ Data not loaded.")
            return

        out_path = out_path or self.csv_path
        self.df.to_csv(out_path, index=False)
        print(f"💾 Saved: {out_path}")

    def __repr__(self):
        return f"BinFile({os.path.basename(self.csv_path)}, rows={len(self.df) if self.df is not None else 0})"


def load_po_files(po_files_names: list[str]) -> dict[str, pd.DataFrame]:

    rtn_df_dict = {}

    for f in po_files_names:
        po = POFile(f)

        # 1️⃣ Read file
        if not po.load():
            print(f"⚠️ {po.name} → Failed to load workbook")
            continue

        # 2️⃣ "格納" Read sheet
        if not po.read_sheet("格納"):
            print(f"⚠️ {po.name} → Failed to read sheet '格納'")
            continue

        # 3️⃣ Extract data
        df = po.extract_data()
        rtn_df_dict[po.name] = df

    return rtn_df_dict


def empty_bins(input_file, unique_bins) -> pd.DataFrame:

    all_empty_bins = EmptyBin()
    ok = all_empty_bins.load()

    if not ok or all_empty_bins.df is None:
        raise RuntimeError(f"❌ Failed to load base CSV: {all_empty_bins.csv_path}")

    df_all_empty_bins = all_empty_bins.df
    print(f"✅ Base CSV loaded: {len(df_all_empty_bins)} rows")

    # Get the Empty file
    df_empty_bins = pd.read_csv(input_file, encoding="utf-8-sig")
    print(f"✅ Input file loaded: {len(df_empty_bins)} rows")

    empty_bin_numbers = df_empty_bins['Bin Number'].unique()
    # print(type(df_all_empty_bins))
    df_all_empty_bins['empty_flag'] = df_all_empty_bins['bin_number'].apply(
        lambda x: 1 if x in empty_bin_numbers else 0
    )
    df_all_empty_bins['criteria_id'] = df_all_empty_bins['bin_number'].apply(
        lambda x: 1 if x in unique_bins else 0
    )

    df_empty_bins = df_all_empty_bins[
        (df_all_empty_bins["empty_flag"] == 1) | (df_all_empty_bins["criteria_id"] == 1)].copy()
    df_empty_bins = df_empty_bins.reset_index(drop=True)
    df_empty_bins["No"] = df_empty_bins.index + 1

    return df_empty_bins

