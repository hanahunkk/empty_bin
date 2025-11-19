import pandas as pd
import os

def update_empty_flag(file_bin_dict_list) -> bool:
    csv_path = "base_empty_bins.csv"
    output_filtered_path = "temp_bins_nonempty.csv"  # ✅ 새로 저장할 파일 이름

    try:
        bins = pd.read_csv(csv_path).fillna("")
    except FileNotFoundError:
        print(f"❌ Cannot find the file: {csv_path}")
        return False
    except Exception as e:
        print(f"❌ CSV reading error: {e}")
        return False

    if "bin_number" not in bins.columns:
        print("❌ There is not 'bin_number' in the CSV file.")
        return False

    if "source_file" not in bins.columns:
        bins["source_file"] = ""
    else:
        bins["source_file"] = bins["source_file"].astype(str)


    valid_items = [
        d for d in file_bin_dict_list
        if isinstance(d, dict) and d.get("file") and d.get("bin")
    ]
    if not valid_items:
        print("⚠️ There are not valid data.")
        return False

    bin_to_file = {d["bin"]: d["file"] for d in valid_items}

    # Update
    for idx, row in bins.iterrows():
        bin_num = str(row["bin_number"]).strip()
        if bin_num in bin_to_file:
            bins.at[idx, "source_file"] = bin_to_file[bin_num]
            # bins.at[idx, "empty_flag"] = 1  # 🔹 필요 시 자동으로 flag도 올림

    bins.to_csv(csv_path, index=False, encoding="utf-8-sig")

    filtered_bins = bins[
        (bins["empty_flag"] == 1) | (bins["source_file"].str.strip() != "")
    ].copy()

    # if os.path.exists(csv_path):
    #     os.remove(csv_path)

    if os.path.exists(output_filtered_path):
        os.remove(output_filtered_path)

    filtered_bins.to_csv(output_filtered_path, index=False, encoding="utf-8-sig")
    return True
