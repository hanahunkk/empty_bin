import os
import pandas as pd
import glob
from empty_bin import EmptyBin, empty_bins


item_category_map = {
    "DRY": ["A10", "A20", "A30"],
    "CHL": ["A40"],
    "FRZ": ["A50"]
}


def make_criteria_ids(input_po_name) -> list[str] | bool:
    default_dir = r"D:\Synology\hunkk\python\tfc\devan\project\EmptyBin\20251111"

    if isinstance(input_po_name, str):
        possible_path = os.path.join(default_dir, input_po_name)
        file_paths = glob.glob(possible_path)
    elif isinstance(input_po_name, (list, tuple)):
        file_paths = [
            os.path.join(default_dir, n)
            for n in input_po_name
            if os.path.exists(os.path.join(default_dir, n))
        ]
    else:
        print("❌ Wrong Input type.")
        return False



    # ✅ PO로 시작하고 .xlsx로 끝나는 파일만 필터
    file_paths = [
        po_file for po_file in file_paths
        if os.path.basename(po_file).upper().startswith("PO") and po_file.lower().endswith(".xlsx")
    ]
    if not file_paths:
        print("❌ There is no files start with PO and end with xlsx.")
        return False

    record_list = []  # 각 파일의 데이터 저장

    for po_file in file_paths:
        try:
            xls = pd.ExcelFile(po_file)
            sheet_names = [s.lower() for s in xls.sheet_names]

            if "格納" not in sheet_names:
                print(f"⚠️ {os.path.basename(po_file)} → '格納' no sheet")
                continue

            df_raw = pd.read_excel(po_file, sheet_name="格納", header=None)
            header_row_index = None
            target_keywords = ["Preferred Bin", "TFC Code", "Pallet#"]

            for i, row in df_raw.iterrows():
                if row.astype(str).apply(lambda x: any(k.lower() in x.lower() for k in target_keywords)).any():
                    header_row_index = i
                    break

            if header_row_index is None:
                print(f"⚠️ {os.path.basename(po_file)}: Header not found")
                continue

            df = pd.read_excel(po_file, sheet_name="格納", header=header_row_index)
            df["source_file"] = os.path.basename(po_file)

            # ✅ 열 이름 후보
            columns_to_keep = {
                "bin": ["preferred bin", "preferred_bin", "bin", "Preferred Bin"]
            }

            col_bin = next((c for c in df.columns if c in columns_to_keep["bin"]), None)

            for _, r in df.iterrows():
                bin_val = str(r.get(col_bin, "")).strip() if col_bin else ""
                if not bin_val or not bin_val.startswith(("A10", "A20", "A30")):
                    continue

                record_list.append({
                    "file": os.path.basename(po_file),
                    "bin": bin_val
                })

            print(f"📘 {os.path.basename(po_file)} → Read complete (header={header_row_index})")

        except Exception as e:
            print(f"❌ {os.path.basename(po_file)} Reading fail: {e}")

    # ✅ 중복 없는 bin 리스트 생성
    unique_bins = sorted({r["bin"] for r in record_list})

    print("\n🔹 Unique Bin List:")
    print(unique_bins)
    print(f"✅ Total unique bins: {len(unique_bins)}")

    return unique_bins  # ✅ bin 리스트 반환


# def make_temp_file(input_file, criteria_id):
def make_temp_file(input_file, bins_list) -> pd.DataFrame:

    all_empty_bins = EmptyBin()
    all_empty_bins.load()
    df_all_empty_bins = all_empty_bins.df

    df_empty_bins = pd.read_csv(input_file)

    category = "DRY"
    valid_prefixes = tuple(item_category_map[category])

    filtered_bins = df_empty_bins[df_empty_bins['Bin Number'].str.startswith(valid_prefixes, na=False)]
    empty_bin_numbers = filtered_bins['Bin Number'].unique()
    df_all_empty_bins['empty_flag'] = df_all_empty_bins['bin_number'].apply(
        lambda x: 1 if x in empty_bin_numbers else 0
    )
    df_all_empty_bins['criteria_id'] = df_all_empty_bins['bin_number'].apply(
        lambda x: 1 if x in bins_list else 0
    )

    df_empty_bins = df_all_empty_bins[(df_all_empty_bins["empty_flag"] == 1) | (df_all_empty_bins["criteria_id"] == 1)].copy()
    df_empty_bins["No"] = range(1, len(df_empty_bins) + 1)
    df_empty_bins.to_excel("df_empty_bins.xlsx", index=False, sheet_name="EmptyBins")

    print(f"df_all_empty_bins: {df_all_empty_bins}")

    return df_empty_bins
    # exit(0)
    #
    #
    #
    #
    #
    # df_all_empty_bins['criteria_id'] = df_all_empty_bins['bin_number'].apply(
    #     lambda x: 1 if x in bins_list else 0
    # )
    # df_empty_bins = df_all_empty_bins[(df_all_empty_bins["empty_flag"] == 1) | (df_all_empty_bins["criteria_id"] == 1)].copy()
    #
    # df_empty_bins.to_csv("df_empty_bins.xlsx", index=False)

    #
    # temp_file = "base_empty_bins.csv"
    #
    # # 1.Read Base Bins
    # # base_bins = pd.read_csv("bins.csv")
    # base_bins = pd.read_csv("bins.csv", header=0, usecols=[0, 1, 2, 3, 4, 5, 6, 7])
    # base_bins.columns = ["No", "bin_number", "empty_flag", "criteria_id", "tfccode",
    #                      "preferred_bin", "source_file", "PO_file"]
    #
    #
    #
    #
    # # 2. Read Empty Bins
    # empty_bins = pd.read_csv(input_file)
    #
    # # Filter empty bins by criteria_id
    # valid_prefixes = ('A10', 'A20', 'A30')
    # filtered_bins = empty_bins[empty_bins['Bin Number'].str.startswith(valid_prefixes, na=False)]
    # empty_bin_numbers = filtered_bins['Bin Number'].unique()
    # base_bins['empty_flag'] = base_bins['bin_number'].apply(lambda x: 1 if x in empty_bin_numbers else 0)
    #
    # base_bins['criteria_id'] = base_bins['bin_number'].apply(
    #     lambda x: 1 if x in bins_list else 0
    # )
    #
    # if os.path.exists(temp_file):
    #     os.remove(temp_file)
    #     print(f"Delete previous file → {temp_file}")
    #
    # # Make the emtpy bin temp file
    # df = base_bins[(base_bins["empty_flag"] == 1) | (base_bins["criteria_id"] == 1)].copy()
    # df.to_csv(temp_file, index=False)

