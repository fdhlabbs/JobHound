# SingleCompanyWindow.py
import tkinter as tk
from tkinter import ttk, messagebox

import model as m


class SingleCompanyWindow(tk.Toplevel):
    def __init__(self, parent, controller, hunt_row_index: int):
        super().__init__(parent)
        self.controller = controller
        self.hunt_row_index = hunt_row_index

        self.title("Company Details")
        self.geometry("700x650")
        self.iconbitmap("icon.ico")

        self.mode_var = tk.StringVar(value="edit")  # "edit" or "switch"
        self.widgets = {}
        self.current_company_id = ""
        self.current_company_row = None

        # ------------------------------------------------------------------
        # Figure out which company this hunt currently uses
        # ------------------------------------------------------------------
        hunt_fields = m.HUNT_FIELDS
        companyid_idx = hunt_fields.index("companyId")

        self.hunt_row = None
        if 0 <= hunt_row_index < len(self.controller.hunt_rows):
            self.hunt_row = self.controller.hunt_rows[hunt_row_index]

        if self.hunt_row and len(self.hunt_row) > companyid_idx:
            self.current_company_id = self.hunt_row[companyid_idx] or ""
        else:
            self.current_company_id = ""

        # Find current company row by id
        company_id_idx = m.COMPANY_FIELDS.index("id")
        self.current_company_row = None
        for crow in self.controller.company_rows:
            if len(crow) > company_id_idx and crow[company_id_idx] == self.current_company_id:
                self.current_company_row = list(crow)
                break

        # Build list of existing company names (for combobox)
        name_idx = m.COMPANY_FIELDS.index("name")
        existing_names = []
        for row in self.controller.company_rows:
            if len(row) > name_idx:
                name = row[name_idx]
                if name and name not in existing_names:
                    existing_names.append(name)

        # ------------------------------------------------------------------
        # Layout
        # ------------------------------------------------------------------
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Mode selection (radio buttons)
        mode_frame = tk.LabelFrame(main_frame, text="Mode")
        mode_frame.pack(fill="x", pady=(0, 10))

        rb_edit = tk.Radiobutton(
            mode_frame,
            text="Edit current company",
            variable=self.mode_var,
            value="edit",
            command=self._apply_mode,
        )
        rb_edit.pack(side="left", padx=(5, 15))

        rb_switch = tk.Radiobutton(
            mode_frame,
            text="Switch to another company",
            variable=self.mode_var,
            value="switch",
            command=self._apply_mode,
        )
        rb_switch.pack(side="left")

        # Form frame
        form = tk.Frame(main_frame)
        form.pack(fill="both", expand=True)

        row = 0

        # Company Name (combobox)
        tk.Label(form, text="Company Name", anchor="w").grid(
            row=row, column=0, sticky="w", pady=4
        )
        cb_name = ttk.Combobox(
            form,
            width=40,
            values=existing_names,
        )
        cb_name.grid(row=row, column=1, sticky="w", pady=4)
        cb_name.bind("<<ComboboxSelected>>", self._on_company_selected)
        self.widgets["name"] = cb_name
        row += 1

        # Industry
        tk.Label(form, text="Industry", anchor="w").grid(
            row=row, column=0, sticky="w", pady=4
        )
        cb_industry = ttk.Combobox(
            form,
            width=40,
            values=["F&B", "Logistics", "IT", "Government"],
        )
        cb_industry.grid(row=row, column=1, sticky="w", pady=4)
        self.widgets["industry"] = cb_industry
        row += 1

        # Description
        tk.Label(form, text="Description", anchor="w").grid(
            row=row, column=0, sticky="nw", pady=4
        )
        txt_desc = tk.Text(form, width=40, height=4)
        txt_desc.grid(row=row, column=1, sticky="w", pady=4)
        self.widgets["description"] = txt_desc
        row += 1

        # Is MNC
        tk.Label(form, text="Is MNC", anchor="w").grid(
            row=row, column=0, sticky="w", pady=4
        )
        cb_is_mnc = ttk.Combobox(
            form,
            width=40,
            values=["Yes", "No"],
            state="readonly",
        )
        cb_is_mnc.grid(row=row, column=1, sticky="w", pady=4)
        self.widgets["isMnc"] = cb_is_mnc
        row += 1

        # Address
        tk.Label(form, text="Address", anchor="w").grid(
            row=row, column=0, sticky="nw", pady=4
        )
        txt_addr = tk.Text(form, width=40, height=3)
        txt_addr.grid(row=row, column=1, sticky="w", pady=4)
        self.widgets["address"] = txt_addr
        row += 1

        # Website
        tk.Label(form, text="Website", anchor="w").grid(
            row=row, column=0, sticky="w", pady=4
        )
        ent_web = tk.Entry(form, width=42)
        ent_web.grid(row=row, column=1, sticky="w", pady=4)
        self.widgets["website"] = ent_web
        row += 1

        # Phone
        tk.Label(form, text="Phone", anchor="w").grid(
            row=row, column=0, sticky="w", pady=4
        )
        ent_phone = tk.Entry(form, width=42)
        ent_phone.grid(row=row, column=1, sticky="w", pady=4)
        self.widgets["phone"] = ent_phone
        row += 1

        # Email
        tk.Label(form, text="Email", anchor="w").grid(
            row=row, column=0, sticky="w", pady=4
        )
        ent_email = tk.Entry(form, width=42)
        ent_email.grid(row=row, column=1, sticky="w", pady=4)
        self.widgets["email"] = ent_email
        row += 1

        # Reputation
        tk.Label(form, text="Reputation (1–5)", anchor="w").grid(
            row=row, column=0, sticky="w", pady=4
        )
        scale_rep = tk.Scale(
            form,
            from_=1,
            to=5,
            orient="horizontal",
            resolution=1,
            length=200,
        )
        scale_rep.set(3)
        scale_rep.grid(row=row, column=1, sticky="w", pady=4)
        self.widgets["reputation"] = scale_rep
        row += 1

        # Prefill from current company if we have one
        self._load_current_company_into_form()

        # ------------------------------------------------------------------
        # Buttons
        # ------------------------------------------------------------------
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", pady=(0, 10), padx=15)

        btn_save = tk.Button(btn_frame, text="Save & Close", command=self._on_save_and_close)
        btn_save.pack(side="right", padx=(5, 0))

        btn_cancel = tk.Button(btn_frame, text="Cancel", command=self._on_cancel)
        btn_cancel.pack(side="right")

        # X button = Cancel (no changes)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        # Apply initial mode (edit)
        self._apply_mode()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_current_company_into_form(self):
        """
        Load self.current_company_row into the widgets (or blanks if none).
        """
        row = self.current_company_row
        fields = m.COMPANY_FIELDS

        def get_val(idx_name: str):
            try:
                idx = fields.index(idx_name)
            except ValueError:
                return ""
            if not row or len(row) <= idx:
                return ""
            return row[idx]

        # Name
        self.widgets["name"].set(get_val("name"))
        # Industry
        self.widgets["industry"].set(get_val("industry"))

        # Description
        desc = get_val("description")
        txt_desc = self.widgets["description"]
        txt_desc.delete("1.0", "end")
        if desc:
            txt_desc.insert("1.0", desc)

        # isMnc
        is_mnc = get_val("isMnc") or "No"
        self.widgets["isMnc"].set(is_mnc)

        # Address
        addr = get_val("address")
        txt_addr = self.widgets["address"]
        txt_addr.delete("1.0", "end")
        if addr:
            txt_addr.insert("1.0", addr)

        # Website
        web = get_val("website")
        ent_web = self.widgets["website"]
        ent_web.delete(0, "end")
        if web:
            ent_web.insert(0, web)

        # Phone
        phone = get_val("phone")
        ent_phone = self.widgets["phone"]
        ent_phone.delete(0, "end")
        if phone:
            ent_phone.insert(0, phone)

        # Email
        email = get_val("email")
        ent_email = self.widgets["email"]
        ent_email.delete(0, "end")
        if email:
            ent_email.insert(0, email)

        # Reputation
        rep = get_val("reputation")
        scale = self.widgets["reputation"]
        try:
            val = int(rep) if rep else 3
        except ValueError:
            val = 3
        scale.set(val)

    def _apply_mode(self):
        """
        Enable/disable fields based on mode:
        - edit   -> all fields editable
        - switch -> only name editable; others disabled + auto-fill from chosen company
        """
        mode = self.mode_var.get()

        if mode == "edit":
            # Everything editable
            self.widgets["name"]["state"] = "normal"
            self.widgets["industry"]["state"] = "normal"
            self.widgets["description"]["state"] = "normal"
            self.widgets["isMnc"]["state"] = "readonly"
            self.widgets["address"]["state"] = "normal"
            self.widgets["website"]["state"] = "normal"
            self.widgets["phone"]["state"] = "normal"
            self.widgets["email"]["state"] = "normal"
            self.widgets["reputation"]["state"] = "normal"

            self._load_current_company_into_form()

        else:  # "switch"
            self.widgets["name"]["state"] = "normal"

            self.widgets["industry"]["state"] = "disabled"
            self.widgets["description"]["state"] = "disabled"
            self.widgets["isMnc"]["state"] = "disabled"
            self.widgets["address"]["state"] = "disabled"
            self.widgets["website"]["state"] = "disabled"
            self.widgets["phone"]["state"] = "disabled"
            self.widgets["email"]["state"] = "disabled"
            self.widgets["reputation"]["state"] = "disabled"

            self._on_company_selected()

    def _on_company_selected(self, event=None):
        """
        When user selects a company name in the combobox:
        - In edit mode: treat this as "current company" to edit
        - In switch mode: show that company's details, read-only
        """
        name = self.widgets["name"].get().strip()
        if not name:
            return

        row = self.controller.find_company_by_name(name)
        if not row:
            return

        self.current_company_row = list(row)
        self._load_current_company_into_form()

    # ------------------------------------------------------------------
    # Save / Cancel
    # ------------------------------------------------------------------
    def _on_save_and_close(self):
        mode = self.mode_var.get()
        if mode == "edit":
            ok = self._save_edit_current()
        else:
            ok = self._save_switch_company()

        if not ok:
            return

        rows = self.controller.finalize_hunt_display_columns()
        self.controller.view.update_hunt_table(rows)

        self.destroy()

    def _on_cancel(self):
        self.destroy()

    # ------------------------------------------------------------------
    # Mode-specific save logic
    # ------------------------------------------------------------------
    def _save_edit_current(self) -> bool:
        """
        Edit the *current* company row's fields (or create if missing).
        """
        name = self.widgets["name"].get().strip()
        industry = self.widgets["industry"].get().strip()
        desc = self.widgets["description"].get("1.0", "end").strip()
        is_mnc = self.widgets["isMnc"].get().strip() or "No"
        addr = self.widgets["address"].get("1.0", "end").strip()
        web = self.widgets["website"].get().strip()
        phone = self.widgets["phone"].get().strip()
        email = self.widgets["email"].get().strip()
        rep = str(self.widgets["reputation"].get())

        if not name:
            messagebox.showwarning("Missing name", "Company Name cannot be empty.")
            return False

        company_fields = m.COMPANY_FIELDS
        id_idx       = company_fields.index("id")
        name_idx     = company_fields.index("name")
        industry_idx = company_fields.index("industry")
        desc_idx     = company_fields.index("description")
        is_mnc_idx   = company_fields.index("isMnc")
        addr_idx     = company_fields.index("address")
        web_idx      = company_fields.index("website")
        rep_idx      = company_fields.index("reputation")
        phone_idx    = company_fields.index("phone")
        email_idx    = company_fields.index("email")

        # Ensure we have a company id
        if not self.current_company_id:
            self.current_company_id = m.new_id()
            companyid_idx = m.HUNT_FIELDS.index("companyId")
            if self.hunt_row and len(self.hunt_row) > companyid_idx:
                self.hunt_row[companyid_idx] = self.current_company_id

        # Find existing row with this id (if any)
        target_index = None
        for i, row in enumerate(self.controller.company_rows):
            if len(row) > id_idx and row[id_idx] == self.current_company_id:
                target_index = i
                break

        width = len(company_fields)
        full_row = [""] * width
        full_row[id_idx]       = self.current_company_id
        full_row[name_idx]     = name
        full_row[industry_idx] = industry
        full_row[desc_idx]     = desc
        full_row[is_mnc_idx]   = is_mnc
        full_row[addr_idx]     = addr
        full_row[web_idx]      = web
        full_row[rep_idx]      = rep
        full_row[phone_idx]    = phone
        full_row[email_idx]    = email

        if target_index is not None:
            self.controller.company_rows[target_index] = full_row
        else:
            self.controller.company_rows.append(full_row)

        return True

    def _save_switch_company(self) -> bool:
        """
        Switch this hunt to another existing company (by name).
        """
        name = self.widgets["name"].get().strip()
        if not name:
            messagebox.showwarning(
                "No company chosen",
                "Please choose an existing company name from the list."
            )
            return False

        row = self.controller.find_company_by_name(name)
        if not row:
            messagebox.showwarning(
                "Unknown company",
                "That company name does not match any existing company.\n"
                "Please pick from the dropdown."
            )
            return False

        company_fields = m.COMPANY_FIELDS
        id_idx = company_fields.index("id")

        if len(row) <= id_idx or not row[id_idx]:
            messagebox.showwarning(
                "Invalid company",
                "The selected company has no valid ID."
            )
            return False

        new_company_id = row[id_idx]

        if self.hunt_row is not None:
            companyid_idx = m.HUNT_FIELDS.index("companyId")

            if len(self.hunt_row) <= companyid_idx:
                self.hunt_row.extend(
                    [""] * (companyid_idx + 1 - len(self.hunt_row))
                )

            self.hunt_row[companyid_idx] = new_company_id

        return True
