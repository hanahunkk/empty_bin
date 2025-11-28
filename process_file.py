from class_bin import BinID
from search_zone import get_zone_number
import os, re
from search_bin import search_bin
import config

def process_bins(df_dict_po_files, df_empty_bins, df_stock_list_heavy) -> bool:
    for search_times in range(1, 3):
        print(f"********************************")
        print(f"🔎 Target Bin: {search_times}")
        print(f"********************************")
        for name, df in df_dict_po_files.items():

            df = df.merge(
                df_stock_list_heavy[['ITEM CODE', 'heavy_flag']],
                left_on='Tfc Code', right_on='ITEM CODE', how='left'
            )
            df.drop(columns=['ITEM CODE'], inplace=True)
            df['heavy_flag'] = df['heavy_flag'].fillna(0).astype(int)

            # print(f"\n📂 Processing PO File: {name} - Total Rows: {df}")

            for code, group in df.groupby("Tfc Code"):
                # group = group.sort_values(
                #     by="Palllet#",
                #     key=lambda x: x.str.contains("ref", case=False, na=False),
                #     ascending=False
                # )
                group = group.sort_values(
                    by="Palllet#",
                    key=lambda x: (
                                      x.str.contains("ref", case=False, na=False).map(lambda v: 0 if v else 1),
                                      x.str.extract(r'(\d+)$')[0].astype(float).fillna(0)
                                  )[1].rank(method="dense") + (
                                      x.str.contains("ref", case=False, na=False).map(lambda v: 0 if v else 1000)),
                    ascending=True
                ).reset_index(drop=True)
                group.index = range(1, len(group) + 1)
                print(f"=================================================================")
                print(f"🔹 {code} - {len(group)} rows")
                print(group[["Palllet#", "Preferred Bin", "格納先"]])
                print(f"=================================================================")
                for idx, row in group.iterrows():
                    # pallet_val = str(row.get("Palllet#"))
                    # has_ref = "ref" in pallet_val.lower()
                    # row["weight"] = weight_val


                    # pallet_val = str(row.get("Palllet#", "")).lower()
                    #
                    # if has_ref:
                    #     if row.get('Tfc Code') in config.REF_LIST:
                    #         config.REF_LIST.remove(row.get('Tfc Code'))
                    #         continue



                    print(f"{idx:03d} | Palllet#: {row.get('Palllet#')} | "
                          f"Tfc Code: {row.get('Tfc Code')} | "
                          f"Preferred Bin: {row.get('Preferred Bin')} | "
                          # f"格納先: {row.get('格納先')} | "
                          # f"Memo: {row.get('Memo')} | "
                          f"Qt: {row.get('Qt')} | "
                          # f"Weight: {row['weight']}"
                          )

                    rtn_check = check_bin(row.get('Preferred Bin'), df_empty_bins)

                    pallet_val = str(row.get("Palllet#", "")).lower()
                    has_ref = "ref" in pallet_val.lower()
                    if has_ref:
                        preferred_bin = str(row.get("Preferred Bin", "")).strip()
                        mask = df_empty_bins["bin_number"] == preferred_bin
                        if mask.any():
                            df_empty_bins.loc[mask, "Palllet#"] = row.get("Palllet#")
                            df_empty_bins.loc[mask, "Tfc Code"] = row.get("Tfc Code")
                            df_empty_bins.loc[mask, "Preferred Bin"] = row.get("Preferred Bin")
                            df_empty_bins.loc[mask, "Qt"] = row.get("Qt")
                            df_empty_bins.loc[mask, "PO name"] = row.get("PO name")

                            print(f"    Skipped 'ref' : bin_number = {preferred_bin}")
                            print(f"-----------------------------------------------------------------")
                        continue

                    if rtn_check:
                        # df_empty_bins = change_empty_bins(row, df_empty_bins)
                        search_bin(row, df_empty_bins, search_times)     # One record
                    else:
                        print(f"    ❌ Invalid Preferred Bin: {row.get('Preferred Bin')}")
                    print(f"-----------------------------------------------------------------")

    return True


def check_bin(code: str, df_empty_bins) -> bool:
    import re

    pattern = r"^[A-Z]{1,2}\d{2}-[A-Z]\d{2}-\d{2}$"

    if not code or str(code).strip().lower() == "nan":
        return False

    code = str(code).strip()
    check1 = bool(re.match(pattern, code))

    if not check1:
        return False

    mask = df_empty_bins["bin_number"] == code

    if not mask.any():
        return False

    pick_reserve = df_empty_bins.loc[mask, "Pick/Reserve"].iloc[0]
    check2 = (str(pick_reserve).strip().upper() == "P")

    return check1 and check2


def check_run(df_empty_bins, po_files_names)->str:
    unique_po_names = df_empty_bins["PO name"].unique()
    messages = []
    for po_name in unique_po_names:
        match1 = re.search(r"(PO\d{5}).*\.xlsx$", po_name)
        if not match1:
            continue
        for po_file in po_files_names:
            filename = os.path.basename(po_file)
            match2 = re.search(r"(PO\d{5}).*\.xlsx$", filename)
            if not match2:
                continue
            if match1 and match2 and match1.group(1) == match2.group(1):
                messages.append(f"Already Done : {filename}")
    if messages:
        msg_text = "\n".join(messages)
        # messagebox.showinfo("PO Match", msg_text)
        return msg_text

    return messages


def change_empty_bins(row, df_empty_bins):
    preferred_bin = row['Preferred Bin']

    matched_row = df_empty_bins[df_empty_bins['bin_number'] == preferred_bin]

    if matched_row.empty:
        return pd.DataFrame()

    bin_type = matched_row['Type'].values[0]

    # 조건 분기
    if bin_type in ["A", "C"]:
        same_type_rows = df_empty_bins[df_empty_bins["Type"] == "A"].copy()
    elif bin_type == "B":
        same_type_rows = df_empty_bins[df_empty_bins["Type"].isin(["A", "B"])].copy()
    else:
        same_type_rows = matched_row.copy()

    print(same_type_rows)
    same_type_rows.to_csv("TEMP.csv")

    exit(0)
    pass