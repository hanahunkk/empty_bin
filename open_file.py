from update_file import update_empty_flag
from empty_bin import empty_bins
import os
import glob
import pandas as pd

#
# # Read PO files
# def open_read_criteria_ids(input_po_name) -> list[str] | bool:
#     default_dir = r"D:\Synology\hunkk\python\tfc\devan\project\EmptyBin\20251022"
#
#     if isinstance(input_po_name, str):
#         possible_path = os.path.join(default_dir, input_po_name)
#         file_paths = glob.glob(possible_path)
#     elif isinstance(input_po_name, (list, tuple)):
#         file_paths = [
#             os.path.join(default_dir, n)
#             for n in input_po_name
#             if os.path.exists(os.path.join(default_dir, n))
#         ]
#     else:
#         print("❌ Wrong Input type.")
#         return False
#
#
#
#     # ✅ PO로 시작하고 .xlsx로 끝나는 파일만 필터
#     file_paths = [
#         po_file for po_file in file_paths
#         if os.path.basename(po_file).upper().startswith("PO") and po_file.lower().endswith(".xlsx")
#     ]
#     if not file_paths:
#         print("❌ There is no files start with PO and end with xlsx.")
#         return False
#
#     record_list = []  # 각 파일의 데이터 저장
#
#     for po_file in file_paths:
#         try:
#             xls = pd.ExcelFile(po_file)
#             sheet_names = [s.lower() for s in xls.sheet_names]
#
#             if "格納" not in sheet_names:
#                 print(f"⚠️ {os.path.basename(po_file)} → '格納' no sheet")
#                 continue
#
#             df_raw = pd.read_excel(po_file, sheet_name="格納", header=None)
#             header_row_index = None
#             target_keywords = ["Preferred Bin", "TFC Code", "Pallet#"]
#
#             for i, row in df_raw.iterrows():
#                 if row.astype(str).apply(lambda x: any(k.lower() in x.lower() for k in target_keywords)).any():
#                     header_row_index = i
#                     break
#
#             if header_row_index is None:
#                 print(f"⚠️ {os.path.basename(po_file)}: Header not found")
#                 continue
#
#             df = pd.read_excel(po_file, sheet_name="格納", header=header_row_index)
#             df["source_file"] = os.path.basename(po_file)
#
#             # ✅ 열 이름 후보
#             columns_to_keep = {
#                 "bin": ["preferred bin", "preferred_bin", "bin", "Preferred Bin"]
#             }
#
#             col_bin = next((c for c in df.columns if c in columns_to_keep["bin"]), None)
#
#             for _, r in df.iterrows():
#                 bin_val = str(r.get(col_bin, "")).strip() if col_bin else ""
#                 if not bin_val or not bin_val.startswith(("A10", "A20", "A30")):
#                     continue
#
#                 record_list.append({
#                     "file": os.path.basename(po_file),
#                     "bin": bin_val
#                 })
#
#             print(f"📘 {os.path.basename(po_file)} → Read complete (header={header_row_index})")
#
#         except Exception as e:
#             print(f"❌ {os.path.basename(po_file)} Reading fail: {e}")
#
#     # ✅ 중복 없는 bin 리스트 생성
#     unique_bins = sorted({r["bin"] for r in record_list})
#
#     print("\n🔹 Unique Bin List:")
#     print(unique_bins)
#     print(f"✅ Total unique bins: {len(unique_bins)}")
#
#     return unique_bins  # ✅ bin 리스트 반환


def open_read_po_files(input_po_name) -> bool:

    default_dir = r"D:\Synology\hunkk\python\tfc\devan\project\EmptyBin\20251023"

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

    file_paths = [
        f for f in file_paths
        if os.path.basename(f).upper().startswith("PO") and f.lower().endswith(".xlsx")
    ]
    if not file_paths:
        print("❌ There is no files start with PO and end with xlsx.")
        return False

    kakuno_ok = []
    kakuno_missing = []

    record_list = []  # ✅ 각 행을 Pallet#, TFC Code, Preferred Bin 세트로 저장

    for po_file in file_paths:
        try:
            xls = pd.ExcelFile(po_file)
            sheet_names = [s.lower() for s in xls.sheet_names]

            if "格納" not in sheet_names:
                print(f"⚠️ {os.path.basename(po_file)} → '格納' no sheet")
                kakuno_missing.append(po_file)
                continue

            kakuno_ok.append(po_file)

            # ✅ 시트 전체를 먼저 읽고 헤더 탐색
            df_raw = pd.read_excel(po_file, sheet_name="格納", header=None)
            header_row_index = None
            target_keywords = ["Preferred Bin", "TFC Code", "Pallet#"]

            for i, row in df_raw.iterrows():
                if row.astype(str).apply(lambda x: any(k.lower() in x.lower() for k in target_keywords)).any():
                    header_row_index = i
                    break

            if header_row_index is None:
                print(f"⚠️ {os.path.basename(po_file)}: Header not found (Preferred Bin / TFC Code / Pallet#)")
                continue

            # ✅ 실제 데이터 읽기
            df = pd.read_excel(po_file, sheet_name="格納", header=header_row_index)
            # df.columns = [str(c).strip().lower() for c in df.columns]  # 🔹 소문자 변환

            df["source_file"] = os.path.basename(po_file)

            # ✅ 가능한 열 이름 후보들
            columns_to_keep = {
                "pallet": ["pallet#", "pallet #", "pallet no", "palletno", "Palllet#"],
                "tfccode": ["tfc code", "tfc_code", "tfc", "Tfc Code"],
                "bin": ["preferred bin", "preferred_bin", "bin", "Preferred Bin"]
            }

            # ✅ 실제 매칭된 컬럼 이름 찾기
            col_pallet = next((c for c in df.columns if c in columns_to_keep["pallet"]), None)
            col_tfc = next((c for c in df.columns if c in columns_to_keep["tfccode"]), None)
            col_bin = next((c for c in df.columns if c in columns_to_keep["bin"]), None)


            # ✅ 각 행을 하나의 딕셔너리로 묶어서 저장
            for _, r in df.iterrows():
                pallet = str(r.get(col_pallet, "")).strip() if col_pallet else ""
                tfccode = str(r.get(col_tfc, "")).strip() if col_tfc else ""
                bin_val = str(r.get(col_bin, "")).strip() if col_bin else ""

                if not bin_val or not bin_val.startswith(("A10", "A20", "A30")):
                    continue

                record_list.append({
                    "file": os.path.basename(po_file),
                    "pallet": pallet,
                    "tfccode": tfccode,
                    "bin": bin_val
                })

            print(f"📘 {os.path.basename(po_file)} → Read complete (header={header_row_index})")
            print("\n📦 Extracted Records (file / pallet / tfccode / bin):")
            print("-" * 70)

            # Process each bin record
            for rec in record_list:
                # print(f"START Record")
                # print(f"{rec['file']} → Pallet: {rec['pallet']}, TFC: {rec['tfccode']}, Bin: {rec['bin']}")
                top3_bins = empty_bins(rec['bin'], po_file)
                # print(f"  top3_bins[0] : {top3_bins[0]} ")


            # print("-" * 70)
            # print(f"✅ Total records: {len(record_list)}")

            # # ✅ 중복 없는 bin 목록 출력
            # unique_bins = sorted({r["bin"] for r in record_list})
            # # print("\n🔹 Unique Bin Numbers:")
            # for unique_bin in unique_bins:
            #     print("  ", unique_bin)

            # print(f"✅ Total unique bins: {len(unique_bins)}")

        except Exception as e:
            print(f"❌ {os.path.basename(po_file)} Reading fail: {e}")



def open_read_excel(input_po_name)->bool:

    default_dir = r"D:\Synology\hunkk\python\tfc\devan\project\EmptyBin\20251023"

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

    file_paths = [
        f for f in file_paths
        if os.path.basename(f).upper().startswith("PO") and f.lower().endswith(".xlsx")
    ]
    if not file_paths:
        print("❌ There is no files start with PO and end with xlsx.")
        return False

    # print("✅ Selected file(s):")
    # for f in file_paths:
    #     print("   -", os.path.basename(f))

    frames = []
    kakuno_ok = []
    kakuno_missing = []

    file_bin_map = {}

    for p in file_paths:
        try:
            xls = pd.ExcelFile(p)
            sheet_names = [s.lower() for s in xls.sheet_names]

            if "格納" not in sheet_names:
                print(f"⚠️ {os.path.basename(p)} → '格納' no sheet")
                kakuno_missing.append(p)
                continue

            kakuno_ok.append(p)

            df_raw = pd.read_excel(p, sheet_name="格納", header=None)

            header_row_index = None
            for i, row in df_raw.iterrows():
                if row.astype(str).str.contains("Preferred Bin", case=False, na=False).any():
                    header_row_index = i
                    break

            if header_row_index is None:
                print(f"⚠️ {os.path.basename(p)}: 'Preferred Bin' no header")
                continue

            df = pd.read_excel(p, sheet_name="格納", header=header_row_index)

            df["source_file"] = os.path.basename(p)
            frames.append(df)

            if "Preferred Bin" in df.columns:
                bins = (
                    df["Preferred Bin"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

                filtered_bins = sorted(
                    [b for b in bins if b.startswith(("A10", "A20", "A30"))]
                )
                file_bin_map[os.path.basename(p)] = filtered_bins
            else:
                file_bin_map[os.path.basename(p)] = []

            print(f"📘 {os.path.basename(p)} → 'Preferred Bin' read (header={header_row_index})")

        except Exception as e:
            print(f"❌ {os.path.basename(p)} Reading fail: {e}")

    if not frames:
        print("❌ No data read.")
        return False


    # ✅ 중복 제거 없이 그대로 출력
    bin_dict_list = []

    for fname, bins in file_bin_map.items():
        if bins:
            for b in bins:
                bin_dict_list.append({
                    "file": fname,
                    "bin": b
                })
        else:
            print(f"⚠️ {fname}: No Preferred Bin found")

    # ✅ 파일명 기준 정렬 (보기 좋게)
    bin_dict_list.sort(key=lambda x: x["file"])

    # ✅ 출력 형식: "파일명 → bin_number"
    for item in bin_dict_list:
        print(f"{item['file']} → {item['bin']}")

    all_bins = set()
    for fname, bins in file_bin_map.items():
        print(f"\n📘 {fname}:")
        if bins:
            for b in bins:
                print("   -", b)
                all_bins.add(b)
                bin_dict_list.append({
                    "file": fname,
                    "bin": b
                })
        else:
            print("   ⚠️ No Preferred Bin starting with A10/A20/A30")

    for item in bin_dict_list:
        print(f"   {item}")

    if not update_empty_flag(bin_dict_list):
        return False

    return True



