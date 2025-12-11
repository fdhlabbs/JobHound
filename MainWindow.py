# MainWindow.py
import tkinter as tk
from tkinter import ttk
import tksheet as tks

import model as m
import SingleCompanyWindow as scw
import debug


class MainWindow:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        # Window display settings
        root.title("JobHound - Job Application Tracking Tool")
        root.geometry("1920x1080")
        root.iconbitmap("icon.ico")


        # Ribbon Bar
        ribbon = tk.Frame(root, bg="#f0f0f0", height=90, bd=1, relief="groove")
        ribbon.pack(fill="x")

        def create_ribbon_button(text, icon, command):
            btn = tk.Button(
                ribbon,
                text=f"{icon}\n{text}",
                font=("Segoe UI", 10),
                width=12,
                height=3,
                compound="top",
                relief="flat",
                command=command
            )
            btn.pack(side="left", padx=5, pady=5)
            return btn

        # Create ribbon buttons with controller actions
        create_ribbon_button("Save",             "💾", self.controller.on_save_clicked)
        create_ribbon_button("New Hunt",         "➕", self.controller.on_new_hunt_clicked)
        create_ribbon_button("AI Job Parse",     "✨", self.controller.ai_jobParse)
        create_ribbon_button("Companies",        "🏢", self.controller.on_companies_clicked)
        create_ribbon_button("Reminders",        "⏰", self.controller.on_reminder_clicked)
        create_ribbon_button("Personal Details", "👨‍💼", self.controller.on_personal_details)

        # Headers for main Hunt sheet
        self.HUNT_HEADERS = [
            "Reminder",
            "Progress",
            "id",
            "Job Title",
            "Job Description",
            "Job Source",
            "Salary BaseMin",
            "Salary BaseMax",
            "Salary IndustryAvg",
            "Salary Expecting",
            "Currency",
            "Ot Rate Ratio",
            "Work Arrangement",
            "Has Health Insurance",
            "companyId",
            "Company Name",
            "Resume",
            "Email",
            "Map",
        ]

        # Build display rows for the main Hunt sheet
        hunt_display_rows = self.controller.finalize_hunt_display_columns()

        # Create the sheet widget
        self.sheet = tks.Sheet(
            root,
            data=hunt_display_rows,
            headers=self.HUNT_HEADERS,
        )

        # Non editable columns
        self.sheet.readonly_columns(
            columns=[0, 1, 2, 14, 15, 16, 17, 18],
            readonly=True
        )

        self.sheet.pack(expand=True, fill="both")

        # Enable basic interactions
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

        # Bindings
        self.sheet.extra_bindings("cell_select",   func=self._on_cell_select)
        self.sheet.extra_bindings("end_edit_cell", func=self._on_end_edit_cell)
        self.sheet.extra_bindings("rc_delete_row", func=self._on_rc_delete_row)

    # ------------------------------------------------------------------
    def update_hunt_table(self, rows):
        """Refresh the main sheet."""
        self.sheet.set_sheet_data(rows)

    # ------------------------------------------------------------------
    def _on_cell_select(self, response):
        """
        Handle clicks on Reminder / Progress / Company Name / Resume / Email / Map.
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

        header = self.HUNT_HEADERS[col]

        hunt_id    = self.sheet.get_cell_data(row, 2)   # id column
        company_id = self.sheet.get_cell_data(row, 14)  # companyId column

        if header == "Reminder" and hunt_id:
            self.controller.open_reminder_window(hunt_id)

        elif header == "Progress" and hunt_id:
            self.controller.open_progress_window(hunt_id)

        elif header == "Company Name" and company_id:
            # Open single-company editor for this hunt row
            scw.SingleCompanyWindow(self.root, self.controller, row)

        elif header == "Resume" and hunt_id:
            self.controller.open_resume_window(hunt_id, company_id)

        elif header == "Email" and hunt_id:
            self.controller.on_email_clicked_for_hunt(hunt_id, company_id)

        elif header == "Map" and hunt_id:
            debug.debug("map", hunt_id, "1")
            self.controller.on_map_clicked_for_hunt(hunt_id, company_id)

    # ------------------------------------------------------------------
    def _on_end_edit_cell(self, response):
        """
        Edit happens here.
        """
        row = response.get("row")
        col = response.get("column")
        new_value = response.get("value")

        if row is None or col is None:
            return

        row = int(row)
        col = int(col)

        # Out of range safety
        if row < 0 or row >= len(self.controller.hunt_rows):
            return

        # Map sheet column -> underlying model column
        # Sheet:  0=Reminder, 1=Progress, 2=id, 3=jobTitle, ...
        # Model:  0=id, 1=jobTitle, ...
        model_col = col - 2
        if model_col < 0 or model_col >= len(m.HUNT_FIELDS):
            return

        hunt_row = self.controller.hunt_rows[row]
        hunt_row[model_col] = new_value
        self.controller.hunt_rows[row] = hunt_row

        # Rebuild the display (so computed columns stay in sync)
        new_rows = self.controller.finalize_hunt_display_columns()
        self.update_hunt_table(new_rows)

    # ------------------------------------------------------------------
    def _on_rc_delete_row(self, response):
        """
        Delete happens here.
        """
        deleted = response.get("deleted", {}).get("rows", {})
        if not deleted:
            return

        # Keys of this dict are the deleted sheet row indices
        sheet_rows = sorted((int(r) for r in deleted.keys()), reverse=True)

        for r in sheet_rows:
            if 0 <= r < len(self.controller.hunt_rows):
                self.controller.hunt_rows.pop(r)

        # Rebuild table after deletion
        new_rows = self.controller.finalize_hunt_display_columns()
        self.update_hunt_table(new_rows)
