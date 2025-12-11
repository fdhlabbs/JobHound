# ReminderWindow.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import tksheet as tks
import model as m


class ReminderWindow(tk.Toplevel):
    """
    Reminder editor window.

    Sheet columns (display):
      0: ID          (readonly)
      1: Hunt Label  (readonly)
      2: Date Time   (editable)
      3: Status      (readonly, but can be set to "Done" via click prompt)
      4: Description (editable)

    Modes:
      - Single-hunt mode: hunt_id is a specific id
      - All-hunt mode:   hunt_id is None
    """

    def __init__(self, parent, controller, hunt_id, display_rows, row_indices_unused):
        super().__init__(parent)
        self.controller = controller
        self.hunt_id = hunt_id  # None => all-hunts mode

        # We ignore row_indices now; we rebuild from sheet on Save & Close.
        self.display_rows = display_rows

        # For all-hunts mode combobox
        self.hunt_labels = []
        self.hunt_label_to_id = {}

        # ------------------------------------------------------------------
        # Window basics
        if self.hunt_id:
            title_label = self.controller._build_hunt_label(self.hunt_id)
            self.title(f"Reminders for {title_label}")
        else:
            self.title("All Reminders")

        self.geometry("950x600")
        self.iconbitmap("icon.ico")

        # When user clicks window "X", we perform Save & Close
        self.protocol("WM_DELETE_WINDOW", self._on_save_and_close)

        # ------------------------------------------------------------------
        # Top frame for sheet
        top_frame = tk.Frame(self)
        top_frame.pack(fill="both", expand=True, padx=10, pady=10)

        headers = ["ID", "Hunt", "Date Time", "Status", "Description"]

        # Expect display_rows in the same order
        self.sheet = tks.Sheet(
            top_frame,
            data=self.display_rows,
            headers=headers,
        )
        self.sheet.pack(fill="both", expand=True)

        # Readonly columns: ID, Hunt label, Status
        self.sheet.readonly_columns(columns=[0, 1, 3], readonly=True)

        # Enable editing of rows + deletion
        self.sheet.enable_bindings((
            "arrowkeys",
            "copy",
            "cut",
            "drag_and_drop",
            "edit_cell",
            "hide_columns",
            "hide_rows",
            "paste",
            "rc_select",
            "rc_delete_row",
            "redo",
            "resize_columns",
            "resize_rows",
            "column_width_resize",
            "row_height_resize",
            "right_click_popup_menu",
            "row_select",
            "show_columns",
            "show_rows",
            "single_select",
            "undo",
        ))

        # When user selects any cell, ask if they want to mark it Done
        self.sheet.extra_bindings("cell_select", func=self._on_cell_select)

        # ------------------------------------------------------------------
        # Bottom form for adding a new reminder
        form_frame = tk.Frame(self)
        form_frame.pack(fill="x", padx=10, pady=10)

        row = 0

        # Hunt selector / label
        if self.hunt_id is None:
            # All-hunts mode: combobox
            tk.Label(form_frame, text="Hunt", anchor="w").grid(
                row=row, column=0, sticky="w", pady=4
            )

            self.hunt_combo = ttk.Combobox(form_frame, width=50)
            self.hunt_combo.grid(row=row, column=1, sticky="w", pady=4, columnspan=4)

            labels, mapping = self.controller.get_all_hunt_choices()
            self.hunt_labels = labels
            self.hunt_label_to_id = mapping
            self.hunt_combo["values"] = self.hunt_labels

            row += 1
        else:
            # Single-hunt mode: show fixed label
            tk.Label(form_frame, text="Hunt", anchor="w").grid(
                row=row, column=0, sticky="w", pady=4
            )
            hunt_label = self.controller._build_hunt_label(self.hunt_id)
            tk.Label(form_frame, text=hunt_label, anchor="w").grid(
                row=row, column=1, sticky="w", pady=4, columnspan=4
            )
            row += 1

        # Date / Time (inline spinboxes)
        tk.Label(form_frame, text="Date / Time", anchor="w").grid(
            row=row, column=0, sticky="w", pady=4
        )

        now = datetime.now()
        self.year_var = tk.IntVar(value=now.year)
        self.month_var = tk.IntVar(value=now.month)
        self.day_var = tk.IntVar(value=now.day)
        self.hour_var = tk.IntVar(value=9)
        self.minute_var = tk.IntVar(value=0)

        # Year
        tk.Label(form_frame, text="Year").grid(row=row, column=1, sticky="w", pady=2)
        tk.Spinbox(
            form_frame,
            from_=now.year - 1,
            to=now.year + 5,
            textvariable=self.year_var,
            width=5,
        ).grid(row=row, column=2, sticky="w", pady=2)

        # Month
        tk.Label(form_frame, text="Month").grid(row=row, column=3, sticky="w", pady=2)
        tk.Spinbox(
            form_frame,
            from_=1,
            to=12,
            textvariable=self.month_var,
            width=3,
        ).grid(row=row, column=4, sticky="w", pady=2)

        # Day
        tk.Label(form_frame, text="Day").grid(row=row, column=5, sticky="w", pady=2)
        tk.Spinbox(
            form_frame,
            from_=1,
            to=31,
            textvariable=self.day_var,
            width=3,
        ).grid(row=row, column=6, sticky="w", pady=2)

        # Hour
        row += 1
        tk.Label(form_frame, text="Hour").grid(row=row, column=1, sticky="w", pady=2)
        tk.Spinbox(
            form_frame,
            from_=0,
            to=23,
            textvariable=self.hour_var,
            width=3,
        ).grid(row=row, column=2, sticky="w", pady=2)

        # Minute
        tk.Label(form_frame, text="Minute").grid(row=row, column=3, sticky="w", pady=2)
        tk.Spinbox(
            form_frame,
            from_=0,
            to=59,
            textvariable=self.minute_var,
            width=3,
        ).grid(row=row, column=4, sticky="w", pady=2)

        row += 1

        # Description
        tk.Label(form_frame, text="Description", anchor="w").grid(
            row=row, column=0, sticky="w", pady=4
        )
        self.desc_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.desc_var, width=60).grid(
            row=row, column=1, sticky="w", pady=4, columnspan=6
        )
        row += 1

        # ------------------------------------------------------------------
        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        tk.Button(btn_frame, text="Add Reminder", command=self._on_add_clicked).pack(
            side="left"
        )

        tk.Button(btn_frame, text="Save & Close", command=self._on_save_and_close).pack(
            side="right"
        )

    # ------------------------------------------------------------------
    # Cell select → mark Done?
    def _on_cell_select(self, response):
        """
        Only react when the Status column (col=3) is clicked.
        """
        row = None
        col = None

        if isinstance(response, dict):
            selected = response.get("selected")
            if selected is not None:
                row = selected.row
                col = selected.column

        if row is None or col is None:
            selected = self.sheet.get_currently_selected()
            if selected is not None:
                row = selected.row
                col = selected.column

        if row is None or col is None:
            return

        # Safety: ensure row in range
        data = self.sheet.get_sheet_data()
        if row < 0 or row >= len(data):
            return

        status_col = 3

        # Only care if user clicked the Status column
        if col != status_col:
            return

        current_status = self.sheet.get_cell_data(row, status_col)

        # Already Done -> nothing to do
        if str(current_status).strip() == "Done":
            return

        # Ask user if they want to mark Done
        result = messagebox.askyesno(
            "Mark as Done",
            "Mark this reminder as Done?",
            parent=self,
        )
        if result:
            self.sheet.set_cell_data(row, status_col, "Done")


    # ------------------------------------------------------------------
    # Add new reminder row
    def _on_add_clicked(self):
        # Determine the hunt id
        if self.hunt_id is not None:
            target_hunt_id = self.hunt_id
        else:
            label = getattr(self, "hunt_combo", None)
            if label is None:
                messagebox.showerror(
                    "Missing hunt",
                    "Please select a hunt.",
                    parent=self,
                )
                return
            label_text = self.hunt_combo.get().strip()
            if not label_text:
                messagebox.showerror(
                    "Missing hunt",
                    "Please select a hunt.",
                    parent=self,
                )
                return
            target_hunt_id = self.hunt_label_to_id.get(label_text)
            if not target_hunt_id:
                messagebox.showerror(
                    "Invalid hunt",
                    "Unknown hunt selected.",
                    parent=self,
                )
                return

        # Build datetime string
        try:
            dt = datetime(
                self.year_var.get(),
                self.month_var.get(),
                self.day_var.get(),
                self.hour_var.get(),
                self.minute_var.get(),
            )
        except ValueError as e:
            messagebox.showerror("Invalid date/time", str(e), parent=self)
            return

        dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        desc = self.desc_var.get().strip()

        # If description and datetime are both empty (shouldn't happen), do nothing
        if not desc and not dt_str:
            return

        # Add via controller. New reminders are always created with status="Pending".
        self.controller.add_reminder_for_hunt(
            target_hunt_id,
            dt_str,
            desc,
        )

        # Refresh our sheet data:
        if self.hunt_id is None:
            # all-hunt mode
            self.display_rows, _ = self.controller.get_reminders_display(None)
        else:
            self.display_rows, _ = self.controller.get_reminders_display(self.hunt_id)

        self.sheet.set_sheet_data(self.display_rows)
        self.sheet.readonly_columns(columns=[0, 1, 3], readonly=True)

        # Clear description; keep date/time near previous
        self.desc_var.set("")

    # ------------------------------------------------------------------
    # Save & Close
    def _on_save_and_close(self):
        """
        Read the current sheet, push changes back to controller.reminder_rows,
        refresh the main Hunt sheet, then close.
        """
        try:
            # NOTE: no return_copy=... here, for your tksheet version
            display_rows = self.sheet.get_sheet_data()

            self.controller.update_reminders_from_display(self.hunt_id, display_rows)
        except Exception as e:
            print("Error in ReminderWindow._on_save_and_close:", e)
        finally:
            self.destroy()

