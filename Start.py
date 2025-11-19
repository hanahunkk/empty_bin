import os
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilenames
from datetime import datetime
from empty_bin import search_main

def open_and_read_excels():
    # 🔹 기본 폴더 경로 지정
    default_dir = r"D:\Synology\hunkk\python\tfc\devan\project\EmptyBin\Test2"

    # 1️⃣ 파일 선택 창 열기
    root = Tk()
    root.withdraw()
    file_paths = askopenfilenames(
        title="PO로 시작하는 엑셀 파일 선택 (복수 선택 가능)",
        filetypes=[("Excel files (PO*.xlsx)", "PO*.xlsx")],
        initialdir=default_dir if os.path.exists(default_dir) else os.path.expanduser("~")
    )
    root.destroy()

    if not file_paths:
        print("❌ 선택한 파일이 없습니다.")
        return

    # 2️⃣ PO로 시작하고 .xlsx로 끝나는 파일만 필터링
    file_paths = [
        f for f in file_paths
        if os.path.basename(f).upper().startswith("PO") and f.lower().endswith(".xlsx")
    ]

    if not file_paths:
        print("❌ PO로 시작하는 .xlsx 파일이 없습니다.")
        return

    print(f"✅ 선택한 파일 수: {len(file_paths)}")
    for p in file_paths:
        print(" -", p)




    # 3️⃣ 각 파일에서 '格納' 시트 읽기
    frames = []
    for p in file_paths:
        try:
            # 엑셀 전체를 일단 읽어옴 (header=None)
            df_raw = pd.read_excel(p, sheet_name="格納", header=None)

            # 'Preferred Bin' 문자열이 포함된 행 찾기
            header_row_index = None
            for i, row in df_raw.iterrows():
                if row.astype(str).str.contains("Preferred Bin", case=False, na=False).any():
                    header_row_index = i
                    break

            if header_row_index is None:
                print(f"⚠️ {os.path.basename(p)}: 'Preferred Bin' 헤더 행을 찾을 수 없습니다.")
                continue

            # 헤더 행 이후부터 데이터 읽기
            df = pd.read_excel(p, sheet_name="格納", header=header_row_index)
            df["source_file"] = os.path.basename(p)

            frames.append(df)
            print(f"📘 {os.path.basename(p)} → 'Preferred Bin' 이후 행 읽기 완료 (header={header_row_index})")

        except ValueError as e:
            print(f"⚠️ {os.path.basename(p)}: '格納' 시트를 찾을 수 없습니다. ({e})")
        except Exception as e:
            print(f"❌ {os.path.basename(p)} 읽기 실패: {e}")

    if not frames:
        print("❌ 읽은 데이터가 없습니다.")
        return





    # 4️⃣ DataFrame 병합
    df_all = pd.concat(frames, ignore_index=True)

    # 5️⃣ 결과 미리보기 + 저장
    print("\n📋 미리보기:")
    print(df_all.head())

    if "Preferred Bin" in df_all.columns and "Tfc Code" in df_all.columns:
        df_valid = df_all[["Tfc Code", "Preferred Bin"]].dropna(subset=["Preferred Bin", "Tfc Code"])

        print("\n⭐ Tfc Code ↔ Preferred Bin 목록:")
        for i, (code, bin_name) in enumerate(zip(df_valid["Tfc Code"], df_valid["Preferred Bin"]), start=1):

            top3_bins = search_main("A10-D08-01")
            print(f"{i:02d}.  {code} : {bin_name} -> {top3_bins[0]}")

    else:
        print("\n⚠️ 'Preferred Bin' 또는 'Tfc Code' 열이 존재하지 않습니다.")

    # # 6️⃣ 'Preferred Bin' 열이 존재하면 출력
    # if "Preferred Bin" in df_all.columns:
    #     preferred_bins = df_all["Preferred Bin"].dropna().unique().tolist()
    #     tfc_code = df_all["Tfc Code"].dropna().unique().tolist()
    #     print("\n⭐ Preferred Bin 목록:")
    #     for i, bin_name in enumerate(preferred_bins, start=1):
    #         print(f"{i:02d}.  {bin_name}")
    # else:
    #     print("\n⚠️ 'Preferred Bin' 열이 존재하지 않습니다.")





    # out_name = os.path.join(default_dir, f"merged_格納_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    # df_all.to_excel(out_name, index=False)
    # print(f"\n💾 '格納' 시트 통합 파일 저장 완료: {out_name}")
    #
    # top3_bins = search_main("A10-D08-01")
    # print(f"성공 ✅ top3_bins={top3_bins}")


if __name__ == "__main__":
    open_and_read_excels()
