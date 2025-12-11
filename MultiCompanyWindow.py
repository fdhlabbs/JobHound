# MultiCompanyWindow.py
import tkinter as tk
from tkinter import ttk, messagebox

import tksheet as tks
import model as m


class MultiCompanyWindow(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.title("All Companies")
        self.geometry("1100x500")
        self.iconbitmap("icon.ico")

        company_fields = m.COMPANY_FIELDS
        self.width = len(company_fields)
        self.id_idx = company_fields.index("id")

        # -------------------------------------------------------------
        # Copy current company_rows into display_rows (normalized)
        # -------------------------------------------------------------
        self.display_rows = []
        for row in self.controller.company_rows:
            r = list(row)
            if len(r) < self.width:
                r = r + [""] * (self.width - len(r))
            elif len(r) > self.width:
                r = r[:self.width]
            self.display_rows.append(r)

        # -------------------------------------------------------------
        # UI
        # -------------------------------------------------------------
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Match COMPANY_FIELDS order:
        # id, name, industry, description, isMnc, address,
        # website, reputation, phone, email
        headers = [
            "id",
            "Name",
            "Industry",
            "Description",
            "Is MNC",
            "Address",
            "Website",
            "Reputation",
            "Phone",
            "Email",
        ]

        self.sheet = tks.Sheet(
            main_frame,
            data=self.display_rows,
            headers=headers,
        )
        self.sheet.pack(fill="both", expand=True)

        # id column visible but read-only
        self.sheet.readonly_columns(columns=[0], readonly=True)

        # Enable editing, but no rc_delete_row -> we control delete via button
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

        # -------------------------------------------------------------
        # Buttons
        # -------------------------------------------------------------
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))

        btn_delete = tk.Button(
            btn_frame, text="Delete Selected", command=self._on_delete_selected
        )
        btn_delete.pack(side="left")

        btn_close = tk.Button(btn_frame, text="Close", command=self._on_close_save)
        btn_close.pack(side="right")

        # X = save & close
        self.protocol("WM_DELETE_WINDOW", self._on_close_save)

    # -------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------
    def _is_company_used(self, company_id: str) -> bool:
        """
        Return True if any hunt row references this company_id.
        """
        if not company_id:
            return False

        hunts = self.controller.hunt_rows
        companyid_idx_in_hunt = m.HUNT_FIELDS.index("companyId")

        for hrow in hunts:
            if len(hrow) > companyid_idx_in_hunt and hrow[companyid_idx_in_hunt] == company_id:
                return True

        return False

    # -------------------------------------------------------------
    # Delete
    # -------------------------------------------------------------
    def _on_delete_selected(self):
        selected = self.sheet.get_currently_selected()
        row = getattr(selected, "row", None)
        if row is None or row < 0 or row >= len(self.display_rows):
            return

        cid = self.display_rows[row][self.id_idx]
        if not cid:
            return

        if self._is_company_used(cid):
            messagebox.showwarning(
                "Cannot delete company",
                "This company is still linked to at least one Hunt.\n"
                "You must reassign or delete those Hunts first."
            )
            return

        # Safe to delete
        del self.display_rows[row]
        self.sheet.set_sheet_data(self.display_rows)
        self.sheet.readonly_columns(columns=[0], readonly=True)

    # -------------------------------------------------------------
    # Close = save to controller.company_rows + refresh main Hunt sheet
    # -------------------------------------------------------------
    def _on_close_save(self):
        try:
            rows = self.sheet.get_sheet_data()

            new_company_rows = []
            for r in rows:
                rr = list(r)
                if len(rr) < self.width:
                    rr = rr + [""] * (self.width - len(rr))
                elif len(rr) > self.width:
                    rr = rr[:self.width]

                cid = rr[self.id_idx].strip() if rr[self.id_idx] else ""
                if not cid:
                    continue

                new_company_rows.append(rr)

            self.controller.company_rows = new_company_rows

            # Refresh main Hunt sheet (company names/email icons, etc. may change)
            hunt_rows = self.controller.finalize_hunt_display_columns()
            self.controller.view.update_hunt_table(hunt_rows)

        except Exception as e:
            print("Error in MultiCompanyWindow._on_close_save:", e)

        finally:
            self.destroy()
