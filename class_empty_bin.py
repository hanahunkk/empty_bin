import os
import config
import pandas as pd
# from bins_weight import make_weight_file


class EmptyBin:



    def __init__(self, input_path=config.EMPTYBIN_DIR):

        # preferred_file = "empty_bins_result20251114.csv"
        # default_file = "bins.csv"
        #
        # preferred_path = os.path.join(input_path, preferred_file)
        # if os.path.exists(preferred_path):
        #     self.csv_path = preferred_path
        # else:
        #     self.csv_path = os.path.join(input_path, default_file)

        self.folder_path = input_path
        self.df = None
        self.csv_path = self.find_result_file()


    def find_result_file(self) -> str:
        """empty_bins_result*.csv 파일이 있으면 그것 사용, 없으면 bins.csv 반환"""
        try:
            for file in os.listdir(self.folder_path):
                if file.startswith("empty_bins_result") and file.endswith(".csv"):
                    full_path = os.path.join(self.folder_path, file)
                    print(f"✅ 결과 파일 사용: {file}")
                    return full_path
        except Exception as e:
            print(f"❌ 폴더 탐색 오류: {e}")

        # 없으면 기본 파일
        fallback = os.path.join(self.folder_path, config.BASE_INPUT_FILE)
        # print("⚠️ 결과 파일 없음 → 기본 bins.csv 사용")
        return fallback


    def load(self) -> bool:
        if not os.path.exists(self.csv_path):
            print(f"❌ File not found: {self.csv_path}")
            return False
        try:
            if "bins.csv" in self.csv_path.lower():
                config.BASE_INPUT_FILE_FLAG = 0
                print("bins.csv 포함됨")
            else:
                config.BASE_INPUT_FILE_FLAG = 1
                print("bins.csv 없음")

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
    def empty_bins(cls, input_file, unique_bins) -> pd.DataFrame:

        all_empty_bins = cls()
        ok = all_empty_bins.load()

        # all_empty_bins.df.to_csv("result_mid3.csv", index=False)
        # exit(0)

        if not ok or all_empty_bins.df is None:
            raise RuntimeError(f"❌ Failed to load base CSV: {all_empty_bins.csv_path}")

        df_all_empty_bins = all_empty_bins.df
        print(f"✅ Base CSV loaded: {len(df_all_empty_bins)} rows")

        if config.BASE_INPUT_FILE_FLAG == 0:

            # Get the Empty file
            df_empty_bins = pd.read_csv(input_file, encoding="utf-8-sig")
            print(f"✅ Input file loaded: {len(df_empty_bins)} rows")

            mask = df_all_empty_bins["criteria_id"] == 0
            df_all_empty_bins.loc[mask, "criteria_id"] = df_all_empty_bins.loc[mask, "bin_number"].apply(
                lambda x: 1 if x in unique_bins else 0
            )

            empty_bin_numbers = df_empty_bins['Bin Number'].unique()
            # print(type(df_all_empty_bins))
            df_all_empty_bins['empty_flag'] = df_all_empty_bins['bin_number'].apply(
                lambda x: 1 if x in empty_bin_numbers else 0
            )

            df_empty_bins = df_all_empty_bins[
                (df_all_empty_bins["empty_flag"] == 1)
                # | (df_all_empty_bins["empty_flag"] == 2)
                | (df_all_empty_bins["criteria_id"] == 1)
                ].copy()
            df_empty_bins = df_empty_bins.reset_index(drop=True)
            df_empty_bins["No"] = df_empty_bins.index + 1

        else:
            df_empty_bins = df_all_empty_bins

        return df_empty_bins


    def __repr__(self):
        return f"BinFile({os.path.basename(self.csv_path)}, rows={len(self.df) if self.df is not None else 0})"

