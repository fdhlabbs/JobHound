# JobAdParseWindow.py
import tkinter as tk
from tkinter import ttk, messagebox

from ai_service import parse_job_ad


class JobAdParseWindow(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parsed_data = None  # will hold {"hunt": {...}, "company": {...}}

        self.title("Parse Job Ad with AI")
        self.geometry("1000x700")
        self.iconbitmap("icon.ico")

        # ======================================================
        # Layout: top = job ad input, bottom = parsed preview
        # ======================================================
        main = tk.Frame(self)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        main.rowconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)
        main.columnconfigure(0, weight=1)

        # -----------------------------
        # Top: Job Ad input
        # -----------------------------
        top_frame = tk.LabelFrame(main, text="Job Advertisement")
        top_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.txt_ad = tk.Text(top_frame, wrap="word", height=12)
        self.txt_ad.pack(fill="both", expand=True, padx=5, pady=5)

        # Parse button
        btn_parse = tk.Button(
            top_frame,
            text="Parse with AI",
            command=self._on_parse_clicked,
        )
        btn_parse.pack(anchor="e", padx=5, pady=(0, 5))

        # -----------------------------
        # Bottom: Parsed preview
        # -----------------------------
        bottom = tk.Frame(main)
        bottom.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=1)
        bottom.rowconfigure(0, weight=1)
        bottom.rowconfigure(1, weight=0)

        # Hunt preview
        hunt_frame = tk.LabelFrame(bottom, text="Parsed Hunt (Job) Fields")
        hunt_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)

        self.txt_hunt = tk.Text(hunt_frame, wrap="word", height=12, state="disabled")
        self.txt_hunt.pack(fill="both", expand=True, padx=5, pady=5)

        # Company preview
        comp_frame = tk.LabelFrame(bottom, text="Parsed Company Fields")
        comp_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)

        self.txt_company = tk.Text(comp_frame, wrap="word", height=12, state="disabled")
        self.txt_company.pack(fill="both", expand=True, padx=5, pady=5)

        # Buttons row
        btn_row = tk.Frame(bottom)
        btn_row.grid(row=1, column=0, columnspan=2, sticky="e", pady=(5, 0))

        self.btn_create = tk.Button(
            btn_row,
            text="Create Hunt & Close",
            command=self._on_create_hunt,
            state="disabled",
        )
        self.btn_create.pack(side="right")

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # =========================================================
    # Parse button
    # =========================================================
    def _on_parse_clicked(self):
        raw = self.txt_ad.get("1.0", "end").strip()
        if not raw:
            messagebox.showerror("No text", "Please paste a job advertisement first.", parent=self)
            return

        # Simple "busy" cursor while waiting
        self.config(cursor="watch")
        self.update_idletasks()

        try:
            parsed = parse_job_ad(raw)
        except Exception as e:
            self.config(cursor="")
            messagebox.showerror("AI Error", f"Failed to parse job ad:\n{e}", parent=self)
            return

        self.config(cursor="")

        # Store and show
        self.parsed_data = parsed
        self._update_preview_widgets()
        self.btn_create.config(state="normal")

    # =========================================================
    # Preview helpers
    # =========================================================
    def _update_preview_widgets(self):
        if not self.parsed_data:
            return

        hunt = self.parsed_data.get("hunt", {})
        company = self.parsed_data.get("company", {})

        # Format nicely (human-readable, not raw JSON)
        hunt_lines = [
            f"jobTitle:            {hunt.get('jobTitle', '')}",
            f"jobDescription:      {hunt.get('jobDescription', '')}",
            f"jobSource:           {hunt.get('jobSource', '')}",
            f"salaryBaseMin:       {hunt.get('salaryBaseMin', '')}",
            f"salaryBaseMax:       {hunt.get('salaryBaseMax', '')}",
            f"salaryIndustryAvg:   {hunt.get('salaryIndustryAvg', '')}",
            f"salaryExpecting:     {hunt.get('salaryExpecting', '')}",
            f"currency:            {hunt.get('currency', '')}",
            f"otRateRatio:         {hunt.get('otRateRatio', '')}",
            f"workArrangement:     {hunt.get('workArrangement', '')}",
            f"hasHealthInsurance:  {hunt.get('hasHealthInsurance', '')}",
        ]
        hunt_text = "\n".join(hunt_lines)

        comp_lines = [
            f"name:         {company.get('name', '')}",
            f"industry:     {company.get('industry', '')}",
            f"description: {company.get('description', '')}",
            f"isMnc:       {company.get('isMnc', '')}",
            f"address:     {company.get('address', '')}",
            f"website:     {company.get('website', '')}",
            f"phone:       {company.get('phone', '')}",
            f"email:       {company.get('email', '')}",
            f"reputation:  {company.get('reputation', '')}",
        ]
        comp_text = "\n".join(comp_lines)

        self._set_text(self.txt_hunt, hunt_text)
        self._set_text(self.txt_company, comp_text)

    def _set_text(self, widget: tk.Text, text: str):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.config(state="disabled")

    # =========================================================
    # Create Hunt in the main table
    # =========================================================
    def _on_create_hunt(self):
        if not self.parsed_data:
            return

        hunt = self.parsed_data.get("hunt", {}) or {}
        company = self.parsed_data.get("company", {}) or {}

        # Build 'data' dict in the SAME shape NewHuntWindow.on_create() sends
        data = {}

        # --- Hunt fields ---
        data["jobTitle"]           = hunt.get("jobTitle", "")
        data["jobDescription"]     = hunt.get("jobDescription", "")
        data["jobSource"]          = hunt.get("jobSource", "")
        data["salaryBaseMin"]      = hunt.get("salaryBaseMin", "")
        data["salaryBaseMax"]      = hunt.get("salaryBaseMax", "")
        data["salaryIndustryAvg"]  = hunt.get("salaryIndustryAvg", "")
        data["salaryExpecting"]    = hunt.get("salaryExpecting", "")
        data["currency"]           = hunt.get("currency", "")
        data["otRateRatio"]        = hunt.get("otRateRatio", "")
        data["workArrangement"]    = hunt.get("workArrangement", "")
        data["hasHealthInsurance"] = hunt.get("hasHealthInsurance", "")

        # --- Company fields ---
        cname = company.get("name", "").strip()
        data["companyName"]        = cname
        data["companyIndustry"]    = company.get("industry", "")
        data["companyDescription"] = company.get("description", "")
        data["companyIsMnc"]       = company.get("isMnc", "")
        data["companyAddress"]     = company.get("address", "")
        data["companyWebsite"]     = company.get("website", "")
        data["companyPhone"]       = company.get("phone", "")
        data["companyEmail"]       = company.get("email", "")
        data["companyReputation"]  = company.get("reputation", "")

        # Decide whether to treat company as existing or new
        company_mode = "new"
        if cname:
            existing = self.controller.find_company_by_name(cname)
            if existing is not None:
                company_mode = "existing"

        data["companyMode"] = company_mode

        # Delegate to controller – this already updates hunt_rows,
        # company_rows, and refreshes the main Hunt sheet.
        self.controller.create_new_hunt(data)

        self.destroy()
