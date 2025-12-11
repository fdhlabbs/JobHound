# ProgressWindow.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime

import tksheet as tks


class ProgressWindow(tk.Toplevel):
    def __init__(self, parent, controller, hunt_id, progress_rows):
        """
        progress_rows is a list-of-lists in display order:
        [ [id, dateTime, status, description], ... ]
        """
        super().__init__(parent)
        self.controller = controller
        self.hunt_id = hunt_id

        self.title(f"Progress - Hunt {hunt_id}")
        self.geometry("800x400")
        self.iconbitmap("icon.ico")

        # --------------------------------------------------------------
        # Sheet showing progress rows: id, Date Time, Status, Description
        # --------------------------------------------------------------
        self.sheet = tks.Sheet(
            self,
            data=progress_rows,
            headers=["id", "Date Time", "Status", "Description"],
        )
        self.sheet.pack(expand=True, fill="both")

        # Make id column (0) read-only, others editable
        self.sheet.readonly_columns(columns=[0], readonly=True)

        # Enable interactions, including row delete via RC menu
        self.sheet.enable_bindings((
            "arrowkeys",
            "copy",
            "cut",
            "paste",
            "edit_cell",
            "undo",
            "redo",
            "row_select",
            "single_select",
            "resize_columns",
            "resize_rows",
            "column_width_resize",
            "row_height_resize",
            "right_click_popup_menu",
            "rc_select",
            "rc_delete_row",
        ))

        # --------------------------------------------------------------
        # Add Progress form (bottom)
        # --------------------------------------------------------------
        form = tk.Frame(self)
        form.pack(fill="x", pady=5, padx=5)

        tk.Label(form, text="Status:").grid(row=0, column=0, sticky="w")
        self.cb_status = ttk.Combobox(
            form,
            width=20,
            values=["Applied", "Interview", "Offer", "Rejected", "On Hold", "Other"],
        )
        self.cb_status.grid(row=0, column=1, sticky="w")
        self.cb_status.set("Applied")

        tk.Label(form, text="Description:").grid(
            row=0, column=2, sticky="w", padx=(10, 0)
        )
        self.ent_desc = tk.Entry(form, width=50)
        self.ent_desc.grid(row=0, column=3, sticky="w")

        btn_add = tk.Button(form, text="Add Progress", command=self.on_add_progress)
        btn_add.grid(row=0, column=4, padx=5)

        btn_save_close = tk.Button(
            form, text="Save & Close", command=self.on_save_and_close
        )
        btn_save_close.grid(row=0, column=5, padx=5)

        # If user clicks window X, treat as Save & Close or "just close"?
        # You said Save & Close, so we wire to the same handler.
        self.protocol("WM_DELETE_WINDOW", self.on_save_and_close)

    # --------------------------------------------------------------
    # Add new progress entry for this hunt
    # --------------------------------------------------------------
    def on_add_progress(self):
        status = self.cb_status.get().strip()
        desc = self.ent_desc.get().strip()

        # If both empty, do nothing
        if not status and not desc:
            return

        dt_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Let controller add row to self.progress_rows and recompute main Hunt sheet
        display_rows = self.controller.add_progress_for_hunt(
            self.hunt_id,
            status,
            desc,
            dt_str=dt_str,
        )

        # Update this window's sheet with fresh rows (including id)
        self.sheet.set_sheet_data(display_rows)
        # Re-apply read-only on id column (tksheet sometimes resets options)
        self.sheet.readonly_columns(columns=[0], readonly=True)

        # Clear form
        self.cb_status.set("Applied")
        self.ent_desc.delete(0, "end")

    # --------------------------------------------------------------
    # Save edits (including deletions) back to controller.progress_rows
    # --------------------------------------------------------------
    def on_save_and_close(self):
        # Get current sheet data (list-of-lists)
        data = self.sheet.get_sheet_data()  # each row: [id, DateTime, Status, Description]

        self.controller.replace_progress_for_hunt_from_display(
            self.hunt_id,
            data,
        )

        self.destroy()
