import os
import pandas as pd


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


    @classmethod
    def load_po_files(cls, po_files_names: list[str]) -> dict[str, pd.DataFrame]:
        rtn_df_dict: dict[str, pd.DataFrame] = {}

        for f in po_files_names:
            po = cls(f)

            if not po.load():
                print(f"⚠️ {po.name} → Failed to load workbook")
                continue

            if not po.read_sheet("格納"):
                print(f"⚠️ {po.name} → Failed to read sheet '格納'")
                continue

            df = po.extract_data()
            rtn_df_dict[po.name] = df

        return rtn_df_dict


    def __repr__(self):
        return f"POFile(name='{self.name}')"
