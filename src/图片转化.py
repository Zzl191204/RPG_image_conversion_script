import os

import tkinter as tk
from tkinter import filedialog, messagebox
import threading


def get_normal_png_header(header_len):
    png_header_hex = '89 50 4E 47 0D 0A 1A 0A 00 00 00 0D 49 48 44 52'
    header_bytes = bytearray(int(b, 16) for b in png_header_hex.split())
    return header_bytes[:header_len]


def restore_png_header(array_buffer):
    if not array_buffer:
        raise ValueError('文件为空或无法读取...')
    png_header = get_normal_png_header(16)
    header_len = len(png_header)
    actual_header = array_buffer[:header_len]
    if actual_header == png_header:
        return array_buffer
    restored_buffer = bytearray(png_header)
    restored_buffer.extend(array_buffer[header_len * 2:])
    return bytes(restored_buffer)


def read_file_as_bytearray(file_path):
    with open(file_path, 'rb') as file:
        return bytearray(file.read())


def process_files(input_directory, output_directory, status_var):
    os.makedirs(output_directory, exist_ok=True)
    for root, _, files in os.walk(input_directory):
        for file in files:
            if file.endswith('.rpgmvp'):
                file_path = os.path.join(root, file)
                try:
                    array_buffer = read_file_as_bytearray(file_path)
                    result = restore_png_header(array_buffer)
                    if result == array_buffer:
                        update_status(status_var, f'跳过未加密文件: {file}')
                        continue
                    relative_path = os.path.relpath(file_path, input_directory)
                    output_file_path = os.path.join(output_directory, relative_path.rsplit('.', 1)[0] + '.png')
                    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                    with open(output_file_path, 'wb') as output_file:
                        output_file.write(result)
                    update_status(status_var, f'正在处理: {file}')
                except Exception as e:
                    update_status(status_var, f'处理文件 {file} 时出错: {e}')
    update_status(status_var, '文件处理完成！')


def update_status(status_var, message):
    def _update():
        status_var.set(message)
    root.after(0, _update)


def select_input_directory():
    input_dir = filedialog.askdirectory()
    if input_dir:
        input_dir_var.set(input_dir)


def select_output_directory():
    output_dir = filedialog.askdirectory()
    if output_dir:
        output_dir_var.set(output_dir)


def start_processing():
    input_dir = input_dir_var.get()
    output_dir = output_dir_var.get()

    if not input_dir or not output_dir:
        messagebox.showerror("错误", "请选定输入目录和输出目录.")
        return

    processing_thread = threading.Thread(target=process_files, args=(input_dir, output_dir, status_var))
    processing_thread.start()


root = tk.Tk()
root.title("RPG Maker MV rpgmvp转png批量工具")
root.geometry("520x200")
root.resizable(False, False)

input_dir_var = tk.StringVar()
output_dir_var = tk.StringVar()
status_var = tk.StringVar()

tk.Label(root, text="输入目录:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
tk.Entry(root, textvariable=input_dir_var, width=50).grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="选择", command=select_input_directory).grid(row=0, column=2, padx=10, pady=10)

tk.Label(root, text="输出目录:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
tk.Entry(root, textvariable=output_dir_var, width=50).grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="选择", command=select_output_directory).grid(row=1, column=2, padx=10, pady=10)

tk.Button(root, text="开始处理", command=start_processing).grid(row=2, column=1, padx=10, pady=20)

status_label = tk.Label(root, textvariable=status_var, anchor='w')
status_label.grid(row=3, column=0, columnspan=3, sticky='ew', padx=10, pady=10)

root.mainloop()

