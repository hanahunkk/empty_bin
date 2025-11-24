from class_bin import BinID
from search_zone import get_zone_number
import os, re
from search_bin import search_bin
import config

def process_bins(df_dict_po_files, df_empty_bins, df_stock_list_heavy) -> bool:
    for search_times in range(1, 3):
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
                print(f"🔹 {code} - {len(group)} rows")
                print(group[["Palllet#", "Preferred Bin", "格納先"]])
                print(f"=================================================================")
                for idx, row in group.iterrows():
                    # pallet_val = str(row.get("Palllet#"))
                    # has_ref = "ref" in pallet_val.lower()
                    # row["weight"] = weight_val
                    pallet_val = str(row.get("Palllet#", "")).lower()
                    has_ref = "ref" in pallet_val.lower()
                    if has_ref:
                        continue

                    # pallet_val = str(row.get("Palllet#", "")).lower()
                    #
                    # if has_ref:
                    #     if row.get('Tfc Code') in config.REF_LIST:
                    #         config.REF_LIST.remove(row.get('Tfc Code'))
                    #         continue

                    rtn_check = check_bin(row.get('Preferred Bin'))
                    print(f"{idx:03d} | Palllet#: {row.get('Palllet#')} | "
                          f"Tfc Code: {row.get('Tfc Code')} | "
                          f"Preferred Bin: {row.get('Preferred Bin')} | "
                          f"格納先: {row.get('格納先')} | "
                          f"Memo: {row.get('Memo')} | "
                          f"Qt: {row.get('Qt')} | "
                          # f"Weight: {row['weight']}"
                          )
                    if rtn_check:
                        # df_empty_bins = change_empty_bins(row, df_empty_bins)
                        search_bin(row, df_empty_bins, search_times)     # One record
                    print(f"-----------------------------------------------------------------")

    return True


def check_bin(code: str) -> bool:
    import re

    pattern = r"^[A-Z]{1,2}\d{2}-[A-Z]\d{2}-\d{2}$"

    if (code is None or
            str(code).strip() == "" or
            str(code).lower() == "nan"):
        return False
    else:
        if isinstance(code, str) and re.match(pattern, code):
            return True
        else:
            return False


# def search_bin(input_record, df_empty_bins, search_times) -> None:
#     input_bin = str(input_record.get('Preferred Bin'))
#     # print(f"type of input_bin ({type(input_bin)})")
#     bin = BinID(input_bin)
#
#     handler = get_location_handler(bin)
#     location_order = handler.get_priority_order()
#     print(f"location_order: {location_order}")
#
#     total_count = 0
#     # found = False
#     for loc in location_order:
#         func = globals().get(f"location_{loc}")
#         if not func:
#             continue
#
#         count_empty = func(input_record, bin, df_empty_bins, search_times)
#         total_count += count_empty
#
#         if total_count > 0:
#             break
#         else:
#             print(f"⚠️ Weight Not enough {total_count}")
#             continue
#
#
# def get_location_handler(bin_id: BinID):
#     from class_location import (
#         LocationA10,
#         LocationA20,
#         LocationA30,
#         LocationA40,
#         LocationA50,
#         LocationBase
#     )
#     mapping = {
#         "A10": LocationA10,
#         "A20": LocationA20,
#         "A30": LocationA30,
#         "A40": LocationA40,
#         "A50": LocationA50,
#     }
#     handler_class = mapping.get(bin_id.location, LocationBase)
#     return handler_class(bin_id)
#
#
# def location_A10(input_record, criteria_id, df_empty_bins, search_times):
#     count_empty = get_zone_number(input_record, criteria_id, df_empty_bins, search_times)
#     return count_empty
#
#
# def location_A20(input_record, criteria_id, df_empty_bins, search_times):
#     count_empty = get_zone_number(input_record, criteria_id, df_empty_bins, search_times)
#     return count_empty
#
#
# def location_A30(input_record, criteria_id,df_empty_bins, search_times):
#     count_empty = get_zone_number(input_record, criteria_id, df_empty_bins, search_times)
#     return count_empty
#
#
# def location_A40(input_record, criteria_id,df_empty_bins, bin_origin):
#     return 0
#
#
# def location_A50(input_record, criteria_id,df_empty_bins, bin_origin):
#     return 0


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

    # Preferred Bin과 일치하는 행 찾기
    matched_row = df_empty_bins[df_empty_bins['bin_number'] == preferred_bin]

    if matched_row.empty:
        print("⚠ 동일한 bin_number를 찾을 수 없습니다.")
        return pd.DataFrame()

    # Type 값 가져오기
    bin_type = matched_row['Type'].values[0]
    print(f"▶ 현재 Type: {bin_type}")

    # 조건 분기
    if bin_type in ["A", "C"]:
        # A 또는 C → A만 출력
        same_type_rows = df_empty_bins[df_empty_bins["Type"] == "A"].copy()
    elif bin_type == "B":
        # B → A와 B 모두 출력
        same_type_rows = df_empty_bins[df_empty_bins["Type"].isin(["A", "B"])].copy()
    else:
        # 정의되지 않은 타입이면 그대로
        same_type_rows = matched_row.copy()

    print("▶ 조건에 맞는 DataFrame:")
    print(same_type_rows)
    same_type_rows.to_csv("TEMP.csv")

    exit(0)
    pass