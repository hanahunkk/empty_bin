import os, re, sys
import tkinter as tk
from tkinter import font
from tkinter import filedialog, messagebox
from process_file import process_bins, check_run
from class_empty_bin import EmptyBin
from save_po_files import save_file
from class_po_file import POFile
from class_stocklist import StockList
import config
from datetime import datetime


log_buffer = []
def log_print(msg):
    # print(msg)  # Console output
    log_buffer.append(msg)

selected_po_paths = []   # PO files
selected_bin_path = ""   # bin file


def check_bins_csv()->bool:
    global selected_bin_path
    fixed_path = os.path.join(config.EMPTYBIN_DIR, "bins.csv")
    if os.path.exists(fixed_path):
        return True
    else:
        messagebox.showerror("Error", f"File not found:\n{fixed_path}")
        return False


def check_empty_bin_csv()->bool:
    global selected_bin_path
    fixed_path = os.path.join(config.EMPTYBIN_DIR, "EmptyBin.csv")
    if os.path.exists(fixed_path):
        selected_bin_path = fixed_path
        return True
    else:
        messagebox.showerror("Error", f"File not found:\n{fixed_path}")
        return False


def select_po_files():
    global selected_po_paths
    file_paths = filedialog.askopenfilenames(
        title="Select PO Excel Files (multiple allowed)",
        filetypes=[("Excel files (PO*.xlsx)", "PO*.xlsx")]
    )
    # file_paths = filedialog.askopenfilenames(
    #     title="Select PO Excel Files (multiple allowed)",
    #     filetypes=[("Excel files", "*.xlsx *.xlsm"), ("All files", "*.*")]
    # )

    if file_paths:
        selected_po_paths = list(file_paths)
        text_purchase_order.delete("1.0", tk.END)
        text_purchase_order.insert(tk.END, "\n".join([os.path.basename(f) for f in file_paths]))

    # if not file_paths:
    #     return
    #
    #
    # pattern = re.compile(r"^PO[A-Za-z0-9]+\.xls[xm]?$")
    #
    # valid_files = []
    # for f in file_paths:
    #     filename = os.path.basename(f).strip()
    #     if pattern.fullmatch(filename):   # ← 반드시 전체 일치 검사(fullmatch)
    #         valid_files.append(f)
    #
    # text_purchase_order.delete("1.0", "end")
    #
    # if valid_files:
    #     selected_po_paths = valid_files
    #     text_purchase_order.insert("end", "\n".join([os.path.basename(f) for f in valid_files]))


def run_process():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # log_print("++++++++++++++++++++++++++++++++++++++++++")
    # log_print(f"🟢 Process started at {timestamp}")
    # log_print("++++++++++++++++++++++++++++++++++++++++++")

    print("++++++++++++++++++++++++++++++++++++++++++")
    print(f"🟢 Process started at {timestamp}")
    print("++++++++++++++++++++++++++++++++++++++++++")


    check1 = check_bins_csv()
    check2 = check_empty_bin_csv()
    if not (check1 and check2):
        sys.exit(1)

    # if not selected_po_paths or not selected_bin_path:
    if not selected_po_paths:
        messagebox.showwarning("Missing File", "⚠️ You must select files!")
        return

    # po_files_names = [os.path.basename(f) for f in selected_po_paths]
    # bin_file_name = os.path.basename(selected_bin_path)

    po_files_names = selected_po_paths
    bin_file_name = selected_bin_path

    # log_print(f"  Selected PO Files: {po_files_names}")
    # log_print(f"  Selected Empty Bin File: {bin_file_name}")
    print(f"Selected PO Files: {po_files_names}")
    print(f"Selected Empty Bin File: {bin_file_name}")

    # Load PO files
    df_dict_po_files = POFile.load_po_files(po_files_names)

    # print(f"po_files_names \n {po_files_names} ")

    all_bins = []
    for name, df in df_dict_po_files.items():
        if "Preferred Bin" in df.columns:
            bins = df["Preferred Bin"].dropna().unique().tolist()
            all_bins.extend(bins)
    unique_bins = sorted(set(all_bins))

    # Load Empty Bin file
    # bin_file_name : EmtpyBin.csv
    df_empty_bins = EmptyBin.empty_bins(bin_file_name)

    # Check duplicate of PO files
    result_string = check_run(df_empty_bins, po_files_names)
    if result_string:
        messagebox.showinfo("PO Match", result_string)
        return

    # Load Stock List
    df_stock_list = StockList.item_standard()
    df_stock_list_heavy = df_stock_list[df_stock_list["heavy_flag"] == 1].copy()
    df_stock_list_heavy = df_stock_list_heavy.reset_index(drop=True)

    print(f"df_stock_list_heavy:\n"
          f'{df_stock_list_heavy}')

    rtn_process = process_bins(df_dict_po_files, df_empty_bins, df_stock_list_heavy)

    # from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # timestamp = datetime.now().strftime("%Y%m%d")
    output_path = config.EMPTYBIN_RESULT_DIR
    output_name = f"empty_bins_result{timestamp}.csv"
    output_path_name = os.path.join(output_path, output_name)

    if os.path.exists(output_path_name):
        os.remove(output_path_name)
        # log_print(f"  🗑️ Deleted existing file: {output_path_name}")
        print(f"🗑️ Deleted existing file: {output_path_name}")

    df_empty_bins.to_csv(output_path_name, index=False)
    # log_print(f"  ✅ Saved new file: {output_path_name}")
    print(f"✅ Saved new file: {output_path_name}")

    save_file(df_empty_bins)

    # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # print("++++++++++++++++++++++++++++++++++++++++++")
    # print(f"🟢 Process ended   at {timestamp}")
    # print("++++++++++++++++++++++++++++++++++++++++++")
    # with open("log_output.txt", "w", encoding="utf-8") as f:
    #     f.write("\n".join(log_buffer))


    # exit(0)
#
def close_app():
    result = messagebox.askyesno("Exit", "Are you sure you want to exit?")
    if result:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("++++++++++++++++++++++++++++++++++++++++++")
        print(f"🟢 Process ended   at {timestamp}")
        print("++++++++++++++++++++++++++++++++++++++++++")
        # with open("log_output.txt", "w", encoding="utf-8") as f:
        #     f.write("\n".join(log_buffer))
        root.destroy()



def check_recieve():
    pass
    # df_empty_bins = EmptyBin.empty_bins(selected_bin_path, 0)
    # show_po_checkboxes(df_empty_bins)


# -------------------------------
# 🎨 Main Window
# -------------------------------
root = tk.Tk()
root.title("File Selector")
root.geometry("640x260")
root.configure(bg="#165A7A")

label_font = font.Font(family="Arial", size=12, weight="bold")
big_font = font.Font(family="Arial", size=10)

# -------------------------------
# 📦 Empty Bin File
# -------------------------------
# tk.Label(
#     root,
#     text="Empty Bin File:",
#     bg="#165A7A",
#     fg="white",
#     font=label_font
# ).grid(row=0, column=0, padx=10, pady=20, sticky="e")
#
# entry_bin = tk.Entry(root, width=55, font=big_font)
# entry_bin.grid(row=0, column=1)
# tk.Button(root, text="🔍 Browse", command=select_empty_bin).grid(row=0, column=2, padx=10)

# -------------------------------
# 📁 PO Files (Multiple)
# -------------------------------
tk.Label(
    root,
    text="PO Files:",
    bg="#165A7A",
    fg="white",
    font=label_font
).grid(row=2, column=0, padx=10, pady=20, sticky="ne")

text_purchase_order = tk.Text(root, width=55, height=5, font=big_font, wrap="none")
text_purchase_order.grid(row=2, column=1, pady=10)

# Optional: Scrollbar
scroll = tk.Scrollbar(root, command=text_purchase_order.yview)
text_purchase_order.config(yscrollcommand=scroll.set)
scroll.grid(row=2, column=2, sticky="ns", pady=10)

tk.Button(root, text="🔍 Find", command=select_po_files).grid(row=2, column=3, padx=5, pady=10, sticky="n")


# -------------------------------
# ▶ Run & ❌ Exit Buttons
# -------------------------------
button_frame = tk.Frame(root, bg="#165A7A")
button_frame.grid(row=1, column=1, pady=10)

tk.Button(
    button_frame,
    text="Check Receive",
    bg="#66CCFF",
    fg="white",
    width=38,
    height=2,
    font=("Arial", 12, "bold"),
    command=check_recieve
).pack(side="top", padx=30)


button_frame = tk.Frame(root, bg="#165A7A")
button_frame.grid(row=3, column=1, pady=10)

tk.Button(
    button_frame,
    text="▶ Run",
    bg="#0A9D58",
    fg="white",
    width=16,
    height=2,
    font=("Arial", 12, "bold"),
    command=run_process
).pack(side="left", padx=30)

tk.Button(
    button_frame,
    text="❌ Exit",
    bg="#C82333",
    fg="white",
    width=15,
    height=2,
    font=("Arial", 12, "bold"),
    command=close_app
).pack(side="right", padx=30)

root.mainloop()
