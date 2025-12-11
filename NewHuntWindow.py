# NewHuntWindow.py
import tkinter as tk
from tkinter import ttk
import tksheet as tks  # still fine even if unused

import model as m


class NewHuntWindow(tk.Toplevel):
    def __init__(self, parent, controller, existing_companies=None):
        super().__init__(parent)
        self.controller = controller
        self.title("New Hunt")
        self.geometry("900x800")
        self.iconbitmap("icon.ico")

        self.inputs = {}            # field_name -> widget (for hunt fields)
        self.company_widgets = {}   # for company fields
        self.company_mode = tk.StringVar(value="new")
        self.existing_companies = existing_companies or []

        # --- Main form frame with left/right split ---
        form_frame = tk.Frame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Configure columns: hunt | separator | company
        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=0)
        form_frame.columnconfigure(2, weight=1)

        hunt_frame = tk.Frame(form_frame)
        hunt_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        sep = ttk.Separator(form_frame, orient="vertical")
        sep.grid(row=0, column=1, sticky="ns", pady=5)

        company_frame = tk.Frame(form_frame)
        company_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0))

        # --- Validators for numeric fields ---
        vcmd_int = (self.register(self._validate_int), "%P")
        vcmd_float = (self.register(self._validate_float), "%P")

        # ==============================================================
        # HUNT FIELDS (LEFT SIDE)
        row_h = 0

        tk.Label(
            hunt_frame, text="Hunt Details", font=("Segoe UI", 10, "bold")
        ).grid(row=row_h, column=0, sticky="w", pady=(0, 8), columnspan=2)
        row_h += 1

        # jobTitle (Entry)
        tk.Label(hunt_frame, text="Job Title", anchor="w").grid(
            row=row_h, column=0, sticky="w", pady=4
        )
        ent_title = tk.Entry(hunt_frame, width=40)
        ent_title.grid(row=row_h, column=1, sticky="w", pady=4)
        self.inputs["jobTitle"] = ent_title
        row_h += 1

        # jobDescription (Text area)
        tk.Label(hunt_frame, text="Job Description", anchor="w").grid(
            row=row_h, column=0, sticky="nw", pady=4
        )
        txt_desc = tk.Text(hunt_frame, width=40, height=5)
        txt_desc.grid(row=row_h, column=1, sticky="w", pady=4)
        self.inputs["jobDescription"] = txt_desc
        row_h += 1

        # jobSource (editable dropdown)
        tk.Label(hunt_frame, text="Job Source", anchor="w").grid(
            row=row_h, column=0, sticky="w", pady=4
        )
        cb_source = ttk.Combobox(
            hunt_frame,
            width=37,
            values=["LinkedIn", "MauKerja", "Indeed"],
        )
        cb_source.set("")
        cb_source.grid(row=row_h, column=1, sticky="w", pady=4)
        self.inputs["jobSource"] = cb_source
        row_h += 1

        # salaryBaseMin (int)
        tk.Label(hunt_frame, text="Salary Base Min", anchor="w").grid(
            row=row_h, column=0, sticky="w", pady=4
        )
        ent_smin = tk.Entry(
            hunt_frame, width=40, validate="key", validatecommand=vcmd_int
        )
        ent_smin.grid(row=row_h, column=1, sticky="w", pady=4)
        self.inputs["salaryBaseMin"] = ent_smin
        row_h += 1

        # salaryBaseMax (int)
        tk.Label(hunt_frame, text="Salary Base Max", anchor="w").grid(
            row=row_h, column=0, sticky="w", pady=4
        )
        ent_smax = tk.Entry(
            hunt_frame, width=40, validate="key", validatecommand=vcmd_int
        )
        ent_smax.grid(row=row_h, column=1, sticky="w", pady=4)
        self.inputs["salaryBaseMax"] = ent_smax
        row_h += 1

        # salaryIndustryAvg (int)
        tk.Label(hunt_frame, text="Salary Industry Avg", anchor="w").grid(
            row=row_h, column=0, sticky="w", pady=4
        )
        ent_savg = tk.Entry(
            hunt_frame, width=40, validate="key", validatecommand=vcmd_int
        )
        ent_savg.grid(row=row_h, column=1, sticky="w", pady=4)
        self.inputs["salaryIndustryAvg"] = ent_savg
        row_h += 1

        # salaryExpecting (int)
        tk.Label(hunt_frame, text="Salary Expecting", anchor="w").grid(
            row=row_h, column=0, sticky="w", pady=4
        )
        ent_sexp = tk.Entry(
            hunt_frame, width=40, validate="key", validatecommand=vcmd_int
        )
        ent_sexp.grid(row=row_h, column=1, sticky="w", pady=4)
        self.inputs["salaryExpecting"] = ent_sexp
        row_h += 1

        # currency (dropdown only)
        tk.Label(hunt_frame, text="Currency", anchor="w").grid(
            row=row_h, column=0, sticky="w", pady=4
        )
        cb_currency = ttk.Combobox(
            hunt_frame,
            width=37,
            values=["MYR", "USD", "SGD"],
            state="readonly",
        )
        cb_currency.set("MYR")
        cb_currency.grid(row=row_h, column=1, sticky="w", pady=4)
        self.inputs["currency"] = cb_currency
        row_h += 1

        # otRateRatio (float)
        tk.Label(hunt_frame, text="OT Rate Ratio", anchor="w").grid(
            row=row_h, column=0, sticky="w", pady=4
        )
        ent_ot = tk.Entry(
            hunt_frame, width=40, validate="key", validatecommand=vcmd_float
        )
        ent_ot.grid(row=row_h, column=1, sticky="w", pady=4)
        self.inputs["otRateRatio"] = ent_ot
        row_h += 1

        # workArrangement (editable dropdown)
        tk.Label(hunt_frame, text="Work Arrangement", anchor="w").grid(
            row=row_h, column=0, sticky="w", pady=4
        )
        cb_wa = ttk.Combobox(
            hunt_frame,
            width=37,
            values=["WFH", "Hybrid", "Onsite"],
        )
        cb_wa.set("")
        cb_wa.grid(row=row_h, column=1, sticky="w", pady=4)
        self.inputs["workArrangement"] = cb_wa
        row_h += 1

        # hasHealthInsurance (Yes/No dropdown only)
        tk.Label(hunt_frame, text="Has Health Insurance", anchor="w").grid(
            row=row_h, column=0, sticky="w", pady=4
        )
        cb_hi = ttk.Combobox(
            hunt_frame,
            width=37,
            values=["Yes", "No"],
            state="readonly",
        )
        cb_hi.set("No")
        cb_hi.grid(row=row_h, column=1, sticky="w", pady=4)
        self.inputs["hasHealthInsurance"] = cb_hi
        row_h += 1

        # ==============================================================
        # COMPANY FIELDS (RIGHT SIDE)
        row_c = 0

        tk.Label(
            company_frame, text="Company", font=("Segoe UI", 10, "bold")
        ).grid(row=row_c, column=0, sticky="w", pady=(0, 8), columnspan=2)
        row_c += 1

        # New / Existing radio buttons
        rb_frame = tk.Frame(company_frame)
        rb_frame.grid(row=row_c, column=0, sticky="w", pady=4, columnspan=2)

        tk.Radiobutton(
            rb_frame,
            text="New",
            variable=self.company_mode,
            value="new",
            command=self._on_company_mode_change,
        ).pack(side="left")

        tk.Radiobutton(
            rb_frame,
            text="Existing",
            variable=self.company_mode,
            value="existing",
            command=self._on_company_mode_change,
        ).pack(side="left")

        row_c += 1

        # Company Name (editable Combobox – can also type new)
        tk.Label(company_frame, text="Company Name", anchor="w").grid(
            row=row_c, column=0, sticky="w", pady=4
        )
        cb_comp_name = ttk.Combobox(
            company_frame,
            width=37,
            values=self.existing_companies,
        )
        cb_comp_name.set("")
        cb_comp_name.grid(row=row_c, column=1, sticky="w", pady=4)
        self.company_widgets["name"] = cb_comp_name
        cb_comp_name.bind("<<ComboboxSelected>>", self._on_existing_company_selected)
        row_c += 1

        # Industry (editable dropdown)
        tk.Label(company_frame, text="Industry", anchor="w").grid(
            row=row_c, column=0, sticky="w", pady=4
        )
        cb_industry = ttk.Combobox(
            company_frame,
            width=37,
            values=["F&B", "Logistics", "IT", "Government"],
        )
        cb_industry.set("")
        cb_industry.grid(row=row_c, column=1, sticky="w", pady=4)
        self.company_widgets["industry"] = cb_industry
        row_c += 1

        # Description (Text)
        tk.Label(company_frame, text="Description", anchor="w").grid(
            row=row_c, column=0, sticky="nw", pady=4
        )
        txt_cdesc = tk.Text(company_frame, width=40, height=4)
        txt_cdesc.grid(row=row_c, column=1, sticky="w", pady=4)
        self.company_widgets["description"] = txt_cdesc
        row_c += 1

        # isMnc (Yes/No dropdown only)
        tk.Label(company_frame, text="Is MNC", anchor="w").grid(
            row=row_c, column=0, sticky="w", pady=4
        )
        cb_is_mnc = ttk.Combobox(
            company_frame,
            width=37,
            values=["Yes", "No"],
            state="readonly",
        )
        cb_is_mnc.set("No")
        cb_is_mnc.grid(row=row_c, column=1, sticky="w", pady=4)
        self.company_widgets["isMnc"] = cb_is_mnc
        row_c += 1

        # Address (Text)
        tk.Label(company_frame, text="Address", anchor="w").grid(
            row=row_c, column=0, sticky="nw", pady=4
        )
        txt_addr = tk.Text(company_frame, width=40, height=3)
        txt_addr.grid(row=row_c, column=1, sticky="w", pady=4)
        self.company_widgets["address"] = txt_addr
        row_c += 1

        # Website (Entry)
        tk.Label(company_frame, text="Website", anchor="w").grid(
            row=row_c, column=0, sticky="w", pady=4
        )
        ent_web = tk.Entry(company_frame, width=40)
        ent_web.grid(row=row_c, column=1, sticky="w", pady=4)
        self.company_widgets["website"] = ent_web
        row_c += 1

        # Phone (Entry)
        tk.Label(company_frame, text="Phone", anchor="w").grid(
            row=row_c, column=0, sticky="w", pady=4
        )
        ent_phone = tk.Entry(company_frame, width=40)
        ent_phone.grid(row=row_c, column=1, sticky="w", pady=4)
        self.company_widgets["phone"] = ent_phone
        row_c += 1

        # Email (Entry)
        tk.Label(company_frame, text="Email", anchor="w").grid(
            row=row_c, column=0, sticky="w", pady=4
        )
        ent_email = tk.Entry(company_frame, width=40)
        ent_email.grid(row=row_c, column=1, sticky="w", pady=4)
        self.company_widgets["email"] = ent_email
        row_c += 1

        # Reputation (slider 1–5)
        tk.Label(company_frame, text="Reputation (1–5)", anchor="w").grid(
            row=row_c, column=0, sticky="w", pady=4
        )
        scale_rep = tk.Scale(
            company_frame,
            from_=1,
            to=5,
            orient="horizontal",
            resolution=1,
            length=200,
        )
        scale_rep.set(3)
        scale_rep.grid(row=row_c, column=1, sticky="w", pady=4)
        self.company_widgets["reputation"] = scale_rep
        row_c += 1

        # ==============================================================
        # Buttons
        # ==============================================================
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", pady=10)

        btn_create = tk.Button(btn_frame, text="Create", command=self.on_create)
        btn_create.pack(side="right", padx=10)

        btn_cancel = tk.Button(btn_frame, text="Cancel", command=self.destroy)
        btn_cancel.pack(side="right")

        # Initialize correct state (New mode)
        self._on_company_mode_change()

    # --- Validation helpers ---
    def _validate_int(self, value_if_allowed: str) -> bool:
        if value_if_allowed == "":
            return True
        return value_if_allowed.isdigit()

    def _validate_float(self, value_if_allowed: str) -> bool:
        if value_if_allowed == "":
            return True
        try:
            float(value_if_allowed)
            return True
        except ValueError:
            return False

    def _on_company_mode_change(self):
        """Enable/disable company fields based on New vs Existing."""
        mode = self.company_mode.get()

        if mode == "new":
            # All company fields editable
            self.company_widgets["name"]["state"] = "normal"
            self.company_widgets["industry"]["state"] = "normal"
            self.company_widgets["description"]["state"] = "normal"
            self.company_widgets["isMnc"]["state"] = "readonly"
            self.company_widgets["address"]["state"] = "normal"
            self.company_widgets["website"]["state"] = "normal"
            self.company_widgets["phone"]["state"] = "normal"
            self.company_widgets["email"]["state"] = "normal"
            self.company_widgets["reputation"]["state"] = "normal"

        else:  # existing
            # Name still editable
            self.company_widgets["name"]["state"] = "normal"

            # Other fields disabled (will auto-fill when company selected)
            self.company_widgets["industry"]["state"] = "disabled"
            self.company_widgets["description"]["state"] = "disabled"
            self.company_widgets["isMnc"]["state"] = "disabled"
            self.company_widgets["address"]["state"] = "disabled"
            self.company_widgets["website"]["state"] = "disabled"
            self.company_widgets["phone"]["state"] = "disabled"
            self.company_widgets["email"]["state"] = "disabled"
            self.company_widgets["reputation"]["state"] = "disabled"

            self._on_existing_company_selected()

    def _on_existing_company_selected(self, event=None):
        """
        When in 'existing' mode and the user picks a company name,
        auto-fill the company fields from the controller, but keep them
        non-editable.
        """
        if self.company_mode.get() != "existing":
            return

        name = self.company_widgets["name"].get().strip()
        if not name:
            return

        row = self.controller.find_company_by_name(name)
        if not row:
            return

        # Map COMPANY_FIELDS -> widgets
        try:
            idx_name        = m.COMPANY_FIELDS.index("name")
            idx_industry    = m.COMPANY_FIELDS.index("industry")
            idx_description = m.COMPANY_FIELDS.index("description")
            idx_is_mnc      = m.COMPANY_FIELDS.index("isMnc")
            idx_address     = m.COMPANY_FIELDS.index("address")
            idx_website     = m.COMPANY_FIELDS.index("website")
            idx_reputation  = m.COMPANY_FIELDS.index("reputation")
            idx_phone       = m.COMPANY_FIELDS.index("phone")
            idx_email       = m.COMPANY_FIELDS.index("email")
        except ValueError:
            return

        # Name
        self.company_widgets["name"].set(
            row[idx_name] if len(row) > idx_name else ""
        )

        # Industry
        self.company_widgets["industry"]["state"] = "normal"
        self.company_widgets["industry"].set(
            row[idx_industry] if len(row) > idx_industry else ""
        )
        self.company_widgets["industry"]["state"] = "disabled"

        # Description
        desc_widget = self.company_widgets["description"]
        desc_widget["state"] = "normal"
        desc_widget.delete("1.0", "end")
        if len(row) > idx_description:
            desc_widget.insert("1.0", row[idx_description])
        desc_widget["state"] = "disabled"

        # isMnc
        self.company_widgets["isMnc"]["state"] = "normal"
        self.company_widgets["isMnc"].set(
            row[idx_is_mnc] if len(row) > idx_is_mnc else ""
        )
        self.company_widgets["isMnc"]["state"] = "disabled"

        # Address
        addr_widget = self.company_widgets["address"]
        addr_widget["state"] = "normal"
        addr_widget.delete("1.0", "end")
        if len(row) > idx_address:
            addr_widget.insert("1.0", row[idx_address])
        addr_widget["state"] = "disabled"

        # Website
        web_widget = self.company_widgets["website"]
        web_widget["state"] = "normal"
        web_widget.delete(0, "end")
        if len(row) > idx_website:
            web_widget.insert(0, row[idx_website])
        web_widget["state"] = "disabled"

        # Phone
        phone_widget = self.company_widgets["phone"]
        phone_widget["state"] = "normal"
        phone_widget.delete(0, "end")
        if len(row) > idx_phone:
            phone_widget.insert(0, row[idx_phone])
        phone_widget["state"] = "disabled"

        # Email
        email_widget = self.company_widgets["email"]
        email_widget["state"] = "normal"
        email_widget.delete(0, "end")
        if len(row) > idx_email:
            email_widget.insert(0, row[idx_email])
        email_widget["state"] = "disabled"

        # Reputation
        rep_widget = self.company_widgets["reputation"]
        rep_widget["state"] = "normal"
        if len(row) > idx_reputation and row[idx_reputation]:
            try:
                rep_widget.set(int(row[idx_reputation]))
            except ValueError:
                rep_widget.set(3)
        else:
            rep_widget.set(3)
        rep_widget["state"] = "disabled"

    def on_create(self):
        data = {}

        # --- Collect hunt fields ---
        for field, widget in self.inputs.items():
            if field == "jobDescription":
                value = widget.get("1.0", "end").strip()
            else:
                value = widget.get().strip()
            data[field] = value

        # --- Collect company fields ---
        mode = self.company_mode.get()
        data["companyMode"] = mode

        data["companyName"]        = self.company_widgets["name"].get().strip()
        data["companyIndustry"]    = self.company_widgets["industry"].get().strip()
        data["companyDescription"] = self.company_widgets["description"].get("1.0", "end").strip()
        data["companyIsMnc"]       = self.company_widgets["isMnc"].get().strip()
        data["companyAddress"]     = self.company_widgets["address"].get("1.0", "end").strip()
        data["companyWebsite"]     = self.company_widgets["website"].get().strip()
        data["companyPhone"]       = self.company_widgets["phone"].get().strip()
        data["companyEmail"]       = self.company_widgets["email"].get().strip()
        data["companyReputation"]  = str(self.company_widgets["reputation"].get())

        # Delegate creation to controller
        self.controller.create_new_hunt(data)
        self.destroy()
