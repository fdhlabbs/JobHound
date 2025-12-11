import tkinter as tk
from tkinter import ttk


class PersonalDetailsWindow(tk.Toplevel):
    def __init__(self, parent, controller, data):
        super().__init__(parent)
        self.controller = controller
        self.data = data

        self.title("Personal Details")
        self.geometry("900x750")
        self.iconbitmap("icon.ico")

        main = tk.Frame(self)
        main.pack(fill="both", expand=True, padx=15, pady=15)

        # ============================
        # BASIC INFO
        # ============================
        self.basic_entries = {}
        basic_fields = [
            ("Name", "name"),
            ("Email", "email"),
            ("LinkedIn ID", "linkedinId"),
            ("GitHub", "githubAcc"),
            ("Phone", "phone"),
        ]

        row = 0
        for label, key in basic_fields:
            tk.Label(main, text=label).grid(row=row, column=0, sticky="w", pady=3)
            ent = tk.Entry(main, width=50)
            ent.grid(row=row, column=1, sticky="w", pady=3)
            ent.insert(0, data.get(key, ""))
            self.basic_entries[key] = ent
            row += 1

        tk.Label(main, text="Address").grid(row=row, column=0, sticky="nw", pady=3)
        self.txt_address = tk.Text(main, width=50, height=3)
        self.txt_address.grid(row=row, column=1)
        self.txt_address.insert("1.0", data.get("address", ""))
        row += 1

        tk.Label(main, text="About").grid(row=row, column=0, sticky="nw", pady=3)
        self.txt_about = tk.Text(main, width=50, height=4)
        self.txt_about.grid(row=row, column=1)
        self.txt_about.insert("1.0", data.get("about", ""))
        row += 2

        # ============================
        # DYNAMIC SECTIONS
        # ============================
        # Education: education / almamater / description
        self.education_rows = self._section(
            parent=main,
            title="Education History",
            items=data.get("education", []),
            fields=["education", "almamater", "description"],
            start_row=row,
        )

        # Space between sections
        row += 5

        # Work: position / company / description
        self.work_rows = self._section(
            parent=main,
            title="Work History",
            items=data.get("work", []),
            fields=["position", "company", "description"],
            start_row=row,
        )

        row += 5

        # Skills: skill / description
        self.skill_rows = self._section(
            parent=main,
            title="Skills",
            items=data.get("skills", []),
            fields=["skill", "description"],
            start_row=row,
        )

        # ============================
        # BUTTONS
        # ============================
        btn = tk.Frame(self)
        btn.pack(fill="x", pady=15)

        tk.Button(btn, text="Cancel", command=self.destroy).pack(side="right", padx=5)
        tk.Button(btn, text="Save & Close", command=self._on_save).pack(side="right")

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # --------------------------------------------------------
    def _section(self, parent, title, items, fields, start_row):
        """
        Build a labelled, dynamic row section.

        `fields` are the keys we store in JSON.
        We also derive human-readable column labels from them.
        """
        frame = tk.LabelFrame(parent, text=title)
        frame.grid(row=start_row, column=0, columnspan=2, sticky="we", pady=10)

        rows = []

        # Map field keys -> nice header labels
        label_map = {
            "education": "Education",
            "almamater": "Institution",
            "description": "Description",
            "position": "Position",
            "company": "Company",
            "skill": "Skill",
        }

        # ----- Header row (row 0 in this frame) -----
        for j, key in enumerate(fields):
            header_text = label_map.get(key, key.title())
            tk.Label(frame, text=header_text).grid(
                row=0, column=j, sticky="w", padx=5, pady=(2, 4)
            )

        # '+' button sits on header row, last column
        tk.Button(frame, text="+", width=3,
                  command=lambda: add_row({})).grid(
            row=0, column=len(fields), padx=5, pady=2
        )

        # ----- Function to add a new data row (starting at row 1) -----
        def add_row(values=None):
            idx = len(rows) + 1   # +1 because row 0 is header
            widgets = {}
            for j, key in enumerate(fields):
                ent = tk.Entry(frame, width=30)
                ent.grid(row=idx, column=j, padx=5, pady=2, sticky="we")
                if values:
                    ent.insert(0, values.get(key, ""))
                widgets[key] = ent
            rows.append(widgets)

        # Pre-fill existing items
        for item in items:
            add_row(item)

        # If there were no existing items, create an empty first row
        if not items:
            add_row({})

        return rows

    # --------------------------------------------------------
    def _on_save(self):
        result = {}

        # Basic fields
        for k, ent in self.basic_entries.items():
            result[k] = ent.get().strip()

        result["address"] = self.txt_address.get("1.0", "end").strip()
        result["about"] = self.txt_about.get("1.0", "end").strip()

        # Education
        result["education"] = []
        for row in self.education_rows:
            d = {k: row[k].get().strip() for k in row}
            if any(d.values()):
                result["education"].append(d)

        # Work
        result["work"] = []
        for row in self.work_rows:
            d = {k: row[k].get().strip() for k in row}
            if any(d.values()):
                result["work"].append(d)

        # Skills
        result["skills"] = []
        for row in self.skill_rows:
            d = {k: row[k].get().strip() for k in row}
            if any(d.values()):
                result["skills"].append(d)

        self.controller.update_personal_details(result)
        self.destroy()
