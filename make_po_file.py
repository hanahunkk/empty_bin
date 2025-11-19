import os
import re
import shutil
from datetime import datetime
import xlwings as xw
from tkinter import Tk, Label, Entry, Button, messagebox

SOURCE_DIR = r"\\Tfc-akl-share\tfc共有\物流部\物流部\ItemStockSearch"
BASE_TEMPLATE = "PO.xlsm"

def find_latest_stocklist(source_dir):
    pattern = re.compile(r"(\d+)-ItemStockList\.xlsx$")
    max_num = -1
    latest_file = None
    for file in os.listdir(source_dir):
        match = pattern.match(file)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
                latest_file = os.path.join(source_dir, file)
    return latest_file


def create_excel_with_macros():
    po_number = entry.get().strip()
    container_name = entry_con.get().strip()

    if not po_number:
        messagebox.showwarning("require", "Enter the PO number.")
        return

    if not container_name:
        messagebox.showwarning("require", "Enter the Container Name.")
        return

    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(current_dir, BASE_TEMPLATE)
    target_path = os.path.join(current_dir, f"PO{po_number}{container_name}.xlsm")

    # 원본 복사 (버튼/VBA 유지)
    shutil.copy(base_path, target_path)

    # Excel 열기 (VBA 포함)
    app = xw.App(visible=False)
    wb_target = app.books.open(target_path)

    # 최신 ItemStockList 찾기
    source_file = find_latest_stocklist(SOURCE_DIR)
    if not source_file:
        messagebox.showerror("Error", "Cannot find ItemStockList File.")
        wb_target.close()
        app.quit()
        return

    wb_src = xw.Book(source_file)
    ws_src = wb_src.sheets["AKL"]
    ws_dst = wb_target.sheets["AKL"]

    # 기존 AKL의 1행 제외 모두 삭제
    last_row = ws_dst.range("A" + str(ws_dst.cells.last_cell.row)).end("up").row
    if last_row > 1:
        ws_dst.range(f"A2:{ws_dst.cells(last_row, ws_dst.cells.last_cell.column).address}").clear_contents()

    # 원본 AKL의 2행부터 복사
    last_row_src = ws_src.range("A" + str(ws_src.cells.last_cell.row)).end("up").row
    ws_src.range(f"A2:{ws_src.cells(last_row_src, ws_src.cells.last_cell.column).address}").copy(ws_dst.range("A2"))

    # Pallet number list 채우기
    ws_pallet = wb_target.sheets["Pallet number list"]
    today = datetime.now().strftime("%Y%m%d")
    row = 2
    seq = 1
    while ws_pallet.range(f"A{row}").value not in [None, ""]:
        ws_pallet.range(f"A{row}").value = f"{today}PO{po_number}-{seq:03d}"
        seq += 1
        row += 1

    wb_src.close()
    wb_target.save()
    wb_target.close()
    app.quit()

    # messagebox.showinfo("Completed", f"✅ '{po_number}.xlsm'")


def exit_program():
    root.destroy()


# GUI
root = Tk()
root.title("Update Stock Items)")
root.geometry("460x240")

Label(root, text="Enter the PO Number(5digit)", font=("Arial", 11)).pack(pady=10)
entry = Entry(root, width=30, font=("Arial", 11))
entry.pack()

Label(root, text="Enter the Container Name", font=("Arial", 11)).pack(pady=10)
entry_con = Entry(root, width=30, font=("Arial", 11))
entry_con.pack()

Button(
    root,
    text="Make File",
    command=create_excel_with_macros,
    bg="#4CAF50", fg="white", font=("Arial", 11), width=35
).pack(pady=10)

Button(
    root,
    text="Exit",
    command=exit_program,
    bg="#d9534f", fg="white", font=("Arial", 11), width=35
).pack(pady=5)

root.mainloop()
