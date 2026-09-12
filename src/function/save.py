import asyncio
import os
import time
import tkinter as tk
from tkinter import filedialog

import aiofiles


file_handle = None
save_dir = ""


def choose_save_dir():
    global save_dir

    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())

    if not save_dir:
        root = tk.Tk()
        root.withdraw()
        save_dir = filedialog.askdirectory(
            title="Choose save location",
            initialdir=os.path.expanduser("~"),
        )
        root.destroy()

        if not save_dir:
            save_dir = os.path.expanduser("~/Documents/captions")
            os.makedirs(save_dir, exist_ok=True)

    return os.path.join(save_dir, f"{timestamp}_captions.txt")


async def save_txt(filename: str, caption: str):
    """Append the caption exactly as processed by the caption hook."""
    async with aiofiles.open(filename, "a", encoding="utf-8") as file:
        await file.write(f"{caption}\n")


async def close_file():
    # Kept for the dashboard shutdown flow; writes open and close per caption.
    global file_handle
    if file_handle is not None:
        await file_handle.close()
        file_handle = None
