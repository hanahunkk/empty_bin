import os
import config
import pandas as pd
# from bins_weight import make_weight_file


class EmptyBin:

    def __init__(self, input_file, input_path=config.EMPTYBIN_DIR, ):
        self.folder_path = input_path
        self.df = None
        self.csv_path = self.csv_path(input_file)

        print(f"csv_path: {self.csv_path}")

    def csv_path(self, input_file) -> str:
        if input_file == "bins.csv":
            self.csv_path = self.path_bins_csv()
        else:
            self.csv_path = self.path_result_csv()

        return self.csv_path


    def path_bins_csv(self) -> str:
        return os.path.join(config.EMPTYBIN_DIR, config.BASE_INPUT_FILE)


    def path_result_csv(self) -> str:
        latest_num = -1
        latest_file = None

        try:
            for file in os.listdir(self.folder_path):
                if file.startswith("empty_bins_result") and file.endswith(".csv"):
                    num_part = file.replace("empty_bins_result", "").replace(".csv", "")

                    if num_part.isdigit():
                        # print(f"num_part: {num_part}")
                        num_val = int(num_part)
                        if num_val > latest_num:
                            latest_num = num_val
                            latest_file = file

            if latest_file:
                # Using the result file
                print(f"✅ Found latest result file: {latest_file}")
                # return os.path.join(self.folder_path, latest_file)
                return os.path.join(config.EMPTYBIN_DIR, latest_file)
            else:
                # Using the original bins.csv file
                print(f"⚠️ No result file found. Using base file: {os.path.join(config.EMPTYBIN_DIR, latest_file)}")

        except Exception as e:
            print(f"❌ Folder Search Error: {e}")


    def load(self, input_csv) -> bool:
        # if not os.path.exists(self.csv_path):
        #     print(f"❌ File not found: {self.csv_path}")
        #     return False
        try:
            if input_csv == "bins.csv":
            # if "bins.csv" in self.csv_path.lower():
                config.BASE_INPUT_FILE_FLAG = 0 # bins.csv
            else:
                config.BASE_INPUT_FILE_FLAG = 1
                config.INPUT_FILE_NAME = self.csv_path.lower()

            self.df = pd.read_csv(
                self.csv_path,
                header=0,
                usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                # encoding="utf-8-sig"
            )
            self.df.columns = [
                "No", "bin_number", "empty_flag", "criteria_id", "Palllet#",
                "Tfc Code", "Preferred Bin", "Memo", "Qt", "Target Bin1",
                "Target Bin2", "Target Bin3", "PO name", "Pick/Reserve", "Type","ZoneType"
            ]

            self.df["No"] = self.df["No"].fillna(0).astype("Int64")
            self.df["empty_flag"] = self.df["empty_flag"].fillna(0).astype("Int64")
            self.df["criteria_id"] = self.df["criteria_id"].fillna(0).astype("Int64")
            self.df["Palllet#"] = self.df["Palllet#"].fillna("").astype(str)
            self.df["Tfc Code"] = self.df["Tfc Code"].fillna("").astype(str)
            self.df["Preferred Bin"] = self.df["Preferred Bin"].fillna("").astype(str)
            self.df["Memo"] = self.df["Memo"].fillna("").astype(str)
            self.df["Qt"] = self.df["Qt"].fillna(0).astype("Int64")
            self.df["Target Bin1"] = self.df["Target Bin1"].fillna("").astype(str)
            self.df["Target Bin2"] = self.df["Target Bin2"].fillna("").astype(str)
            self.df["Target Bin3"] = self.df["Target Bin3"].fillna("").astype(str)
            self.df["PO name"] = self.df["PO name"].fillna("").astype(str)
            self.df["Pick/Reserve"] = self.df["Pick/Reserve"].fillna("").astype(str)
            self.df["Type"] = self.df["Type"].fillna("").astype(str)
            self.df["ZoneType"] = self.df["ZoneType"].fillna("").astype(str)

            # self.df.to_csv("result_mid2.csv", index=False)
            # exit(0)

            print(f"✅ Loaded {len(self.df)} rows from {os.path.basename(self.csv_path)}")
            return True

        except Exception as e:
            print(f"❌ Failed to load {self.csv_path}: {e}")
            return False

    # ---------------------------------------------------
    # 🔸 function methods
    # ---------------------------------------------------
    def get_by_criteria(self, criteria_id: str):
        if self.df is None:
            print("⚠️ Data not loaded.")
            return None
        result = self.df[self.df["criteria_id"] == criteria_id]
        return result

    def get_unique_preferred_bins(self):
        if self.df is None:
            print("⚠️ Data not loaded.")
            return []
        return sorted(self.df["preferred_bin"].dropna().unique().tolist())

    def count_empty_bins(self):
        if self.df is None:
            print("⚠️ Data not loaded.")
            return 0
        return int((self.df["empty_flag"] == 1).sum())

    def save(self, out_path=None):
        if self.df is None:
            print("⚠️ Data not loaded.")
            return

        out_path = out_path or self.csv_path
        self.df.to_csv(out_path, index=False)
        print(f"💾 Saved: {out_path}")


    @classmethod
    # def empty_bins(cls, input_file, unique_bins) -> pd.DataFrame:
    def empty_bins(cls, input_file) -> pd.DataFrame:

        all_empty_bins = cls("bins.csv")
        ok = all_empty_bins.load("bins.csv")  # Load the base bins.csv file
        if not ok or all_empty_bins.df is None:
            raise RuntimeError(f"❌ Failed to load base CSV: {all_empty_bins.csv_path}")
        df_all_empty_bins = all_empty_bins.df
        print(f"all_empty_bins: {all_empty_bins}")

        input_file = os.path.join(config.EMPTYBIN_DIR, config.EMPTYBIN_FILE)
        df_empty_bins = pd.read_csv(input_file, encoding="utf-8-sig")
        empty_bin_numbers = df_empty_bins['Bin Number'].unique()
        df_empty_bins = df_all_empty_bins[
            (
                    df_all_empty_bins['bin_number'].isin(empty_bin_numbers) |
                    (df_all_empty_bins['Pick/Reserve'].astype(str).str.strip() == "P")
            )
        ].copy()
        df_empty_bins = df_empty_bins.reset_index(drop=True)
        df_empty_bins["No"] = (df_empty_bins.index + 1).astype("Int64")
        df_empty_bins.to_csv("TEMP_empty_bins.csv", index=False)
        print(f"empty_bin_numbers: {len(df_empty_bins)}")

        result_empty_bins = cls("result.csv")
        ok = result_empty_bins.load("result.csv")
        if not ok or result_empty_bins.df is None:
            return df_empty_bins

        df_result_empty_bins = result_empty_bins.df
        print(f"result_empty_bins: {df_result_empty_bins}")

        po_not_empty = ~(
                df_result_empty_bins['PO name'].isna() |
                (df_result_empty_bins['PO name'].astype(str).str.strip() == "")
        )

        df_po_rows = df_result_empty_bins[po_not_empty].copy()

        df_merged = df_empty_bins.merge(
            df_po_rows,
            on='bin_number',
            how='left',
            suffixes=('', '_new')
        )

        for col in df_empty_bins.columns:
            if col != 'bin_number':
                new_col = col + '_new'
                if new_col in df_merged.columns:
                    df_merged[col] = df_merged[new_col].combine_first(df_merged[col])
                    df_merged.drop(columns=[new_col], inplace=True)

        df_empty_bins = df_merged
        # df_empty_bins.to_csv("TEMP2_empty_bins.csv", index=False)

        # exit(0)
        #
        # df_all_empty_bins = all_empty_bins.df
        # print(f"✅ Base CSV loaded: {len(df_all_empty_bins)} rows")
        #
        #
        #
        # if config.BASE_INPUT_FILE_FLAG == 1 or config.BASE_INPUT_FILE_FLAG == 0:
        #     # Get the Empty file
        #     df_empty_bins = pd.read_csv(input_file, encoding="utf-8-sig")
        #     print(f"✅ Input file loaded: {len(df_empty_bins)} rows")
        #
        #     empty_bin_numbers = df_empty_bins['Bin Number'].unique()
        #
        #     po_not_empty = ~(
        #             df_all_empty_bins['PO name'].isna() |
        #             (df_all_empty_bins['PO name'].astype(str).str.strip() == "")
        #     )
        #
        #     # 2) PO name 이 비어 있지 않은 행은 empty_flag = 0
        #     # df_all_empty_bins.loc[po_not_empty, 'empty_flag'] = 0
        #     df_all_empty_bins.loc[
        #         po_not_empty & (df_all_empty_bins['empty_flag'] != 2),
        #         'empty_flag'
        #     ] = 0
        #
        #     df_empty_bins = df_all_empty_bins[
        #         (
        #                 df_all_empty_bins['bin_number'].isin(empty_bin_numbers) |
        #                 (df_all_empty_bins['Pick/Reserve'].astype(str).str.strip() == "P")
        #         )
        #         # &
        #         # (
        #         #         df_all_empty_bins['PO name'].isna() |
        #         #         (df_all_empty_bins['PO name'].astype(str).str.strip() == "")
        #         # )
        #         ].copy()
        #
        #     df_empty_bins = df_empty_bins.reset_index(drop=True)
        #     df_empty_bins["No"] = df_empty_bins.index + 1
        #
        #     # df_empty_bins.to_csv("TEMP1.csv")
        #     # exit(0)
        #
        # else:
        #     # unique_po_names = df_all_empty_bins["PO name"].dropna().unique()
        #
        #     unique_po_names = (
        #         df_all_empty_bins["PO name"]
        #         .dropna()  # NaN 제거
        #         .astype(str)
        #         .str.strip()  # 앞뒤 공백 제거
        #     )
        #     unique_po_names = unique_po_names[unique_po_names != ""]
        #     unique_po_names = unique_po_names.unique().tolist()
        #
        #     show_po_checkboxes(os.path.basename(config.INPUT_FILE_NAME),
        #                        unique_po_names,
        #                        df_all_empty_bins)
        #     print(f"unique_po_names:{unique_po_names}")
        #     if os.path.exists("TEMP.csv"):
        #         os.remove("TEMP.csv")
        #     df_all_empty_bins.to_csv("TEMP.csv")
        #     # df_empty_bins = df_all_empty_bins
        #
        #     exit(0)

        return df_empty_bins


    def __repr__(self):
        return f"BinFile({os.path.basename(self.csv_path)}, rows={len(self.df) if self.df is not None else 0})"

import tkinter as tk
import re

# def show_po_checkboxes(input_file, unique_po_names, df_all_empty_bins):
def show_po_checkboxes(df_empty_bins):
    win = tk.Tk()
    win.title("Check Receive")

    win.geometry("400x200")
    win.resizable(False, False)

    var_dict: dict[str, tk.IntVar] = {}

    unique_po_names = (
        df_empty_bins["PO name"]
        .dropna()   # remove NaN
        .astype(str).str.strip()  # remove Spaces
        .replace("", pd.NA)  # remove empty strings
        .dropna()  # remove NaN again
        .unique()  # remove duplicates
        .tolist()  # transform to list
    )

    for name in unique_po_names:
        var = tk.IntVar(value=0)  # 0: unchecked, 1: checked
        chk = tk.Checkbutton(win, text=name, variable=var, onvalue=1, offvalue=0)
        chk.pack(anchor="w")
        var_dict[name] = var

    def confirm():
        selected_raw = [name for name, var in var_dict.items() if var.get() == 1]

        selected_po = [extract_po_name(name) for name in selected_raw]

        selected_po = [po for po in selected_po if po is not None]


        # df_all_empty_bins.loc[
        #     df_all_empty_bins["PO name"].isin(selected_po),
        #     "empty_flag"
        # ] = 0

        print(df_all_empty_bins[df_all_empty_bins["PO name"].isin(selected_po)])

    tk.Button(win, text="Confirm", command=confirm).pack(pady=10)

    win.mainloop()




