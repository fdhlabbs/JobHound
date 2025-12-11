# ResumeWindow.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
import os
import re

import resume_service
from app_paths import OUTPUT_DIR

class ResumeWindow(tk.Toplevel):
    def __init__(self, parent, controller, hunt_id, context):
        super().__init__(parent)
        self.controller = controller
        self.hunt_id = hunt_id
        # context: {"personal": {...}, "hunt": {...}, "company": {...}}
        self.context = context

        self.title("Generate Resume")
        self.geometry("900x700")
        self.iconbitmap("icon.ico")

        # ======================================================
        # Layout: top = context (read-only), bottom = preferences
        # ======================================================
        main = tk.Frame(self)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        main.rowconfigure(0, weight=2)
        main.rowconfigure(1, weight=1)
        main.columnconfigure(0, weight=1)

        # -----------------------------
        # Top: context summary (read-only)
        # -----------------------------
        top_frame = tk.LabelFrame(main, text="Application Context (read-only)")
        top_frame.grid(row=0, column=0, sticky="nsew")

        self.txt_context = tk.Text(top_frame, wrap="word")
        self.txt_context.pack(fill="both", expand=True)
        self.txt_context.config(state="disabled")

        # -----------------------------
        # Bottom: preferences + button
        # -----------------------------
        pref_frame = tk.LabelFrame(main, text="Resume Preferences (optional)")
        pref_frame.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        pref_frame.columnconfigure(1, weight=1)
        pref_frame.rowconfigure(3, weight=1)  # notes grows

        row = 0

        tk.Label(pref_frame, text="Target role / headline").grid(
            row=row, column=0, sticky="w", pady=3
        )
        self.ent_target_role = tk.Entry(pref_frame)
        self.ent_target_role.grid(row=row, column=1, sticky="we", pady=3)
        row += 1

        tk.Label(pref_frame, text="Tone (e.g. concise, formal)").grid(
            row=row, column=0, sticky="w", pady=3
        )
        self.ent_tone = tk.Entry(pref_frame)
        self.ent_tone.grid(row=row, column=1, sticky="we", pady=3)
        row += 1

        tk.Label(pref_frame, text="Skills to emphasise (comma-separated)").grid(
            row=row, column=0, sticky="w", pady=3
        )
        self.ent_skills = tk.Entry(pref_frame)
        self.ent_skills.grid(row=row, column=1, sticky="we", pady=3)
        row += 1

        tk.Label(pref_frame, text="Extra notes for AI").grid(
            row=row, column=0, sticky="nw", pady=3
        )
        self.txt_notes = tk.Text(pref_frame, height=4)
        self.txt_notes.grid(row=row, column=1, sticky="nsew", pady=3)
        row += 1

        # Buttons row (no explicit Close – use window X)
        btn_row = tk.Frame(pref_frame)
        btn_row.grid(row=row, column=0, columnspan=2, sticky="e", pady=(5, 0))

        self.btn_generate = tk.Button(
            btn_row,
            text="Generate Resume",
            command=self._on_generate_clicked,
        )
        self.btn_generate.pack(side="right")

        # X button just closes
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        # Now that widgets exist, fill context + default headline
        self._populate_summary()
        self._prefill_target_role()

    # =========================================================
    # Context summary (top text area)
    # =========================================================
    def _populate_summary(self):
        """
        Fill the read-only top text box with PERSONAL / HUNT / COMPANY
        information from self.context.
        """
        personal = self.context.get("personal", {}) or {}
        hunt     = self.context.get("hunt", {}) or {}
        company  = self.context.get("company", {}) or {}

        lines = []

        # PERSONAL
        lines.append("PERSONAL")
        lines.append(f"  Name:     {personal.get('name', '')}")
        lines.append(f"  Email:    {personal.get('email', '')}")
        lines.append(f"  Phone:    {personal.get('phone', '')}")
        lines.append(f"  LinkedIn: {personal.get('linkedinId', '')}")
        lines.append(f"  GitHub:   {personal.get('githubAcc', '')}")
        lines.append("")

        # HUNT / JOB
        lines.append("HUNT / JOB")
        lines.append(f"  Job Title:    {hunt.get('jobTitle', '')}")
        lines.append("  Description:")
        desc = hunt.get("jobDescription", "") or ""
        if desc:
            for line in desc.splitlines():
                lines.append(f"    {line}")
        lines.append("")

        # COMPANY
        lines.append("COMPANY")
        lines.append(f"  Name:    {company.get('name', '')}")
        lines.append(f"  Address: {company.get('address', '')}")
        comp_desc = company.get("description", "") or ""
        if comp_desc:
            lines.append("  Description:")
            for line in comp_desc.splitlines():
                lines.append(f"    {line}")

        text = "\n".join(lines)

        self.txt_context.config(state="normal")
        self.txt_context.delete("1.0", "end")
        self.txt_context.insert("1.0", text)
        self.txt_context.config(state="disabled")

    def _prefill_target_role(self):
        """Pre-fill the target-role field from the job title/company (optional)."""
        hunt    = self.context.get("hunt", {}) or {}
        company = self.context.get("company", {}) or {}

        job_title = (hunt.get("jobTitle") or "").strip()
        company_name = (company.get("name") or "").strip()

        if not self.ent_target_role.get().strip():
            if job_title and company_name:
                self.ent_target_role.insert(0, f"{job_title} – {company_name}")
            elif job_title:
                self.ent_target_role.insert(0, job_title)

    # -------------------------------------------
    def _collect_prefs(self) -> Dict[str, Any]:
        """
        Gather one-off user preferences from the bottom form.
        All fields are optional.
        """
        prefs = {
            "targetRole": self.ent_target_role.get().strip(),
            "tone": self.ent_tone.get().strip(),
            "skillsToEmphasise": self.ent_skills.get().strip(),
            "notes": self.txt_notes.get("1.0", "end").strip(),
        }
        return prefs

    # -------------------------------------------
    def _safe_slug(self, value: str, fallback: str = "resume") -> str:
        value = (value or "").strip()
        if not value:
            value = fallback
        value = re.sub(r"[^A-Za-z0-9]+", "_", value)
        value = value.strip("_")
        return value or fallback

    # -------------------------------------------
    def _on_generate_clicked(self):
        # Disable button while working
        self.btn_generate.config(state="disabled")
        self.config(cursor="watch")
        self.update_idletasks()

        try:
            prefs = self._collect_prefs()
            context = {
                "personal": self.context.get("personal", {}),
                "hunt": self.context.get("hunt", {}),
                "company": self.context.get("company", {}),
                "prefs": prefs,
            }

            # Call AI to get structured resume JSON
            resume_json = resume_service.generate_resume_structure(context)

            # Build output path: output/resumes/<job>_<company>_<timestamp>.docx
            output_dir = OUTPUT_DIR

            hunt = self.context.get("hunt", {}) or {}
            company = self.context.get("company", {}) or {}

            job_title = hunt.get("jobTitle", "") or ""
            company_name = company.get("name", "") or ""

            slug_job = self._safe_slug(job_title, "job")
            slug_company = self._safe_slug(company_name, "company")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            filename = f"{slug_job}_{slug_company}_{timestamp}.docx"
            out_path = output_dir / filename

            resume_service.build_resume_docx(resume_json, out_path)

            # Try to open file directly (Windows-friendly)
            try:
                os.startfile(out_path)  # type: ignore[attr-defined]
            except Exception:
                # Non-Windows or failure to open: ignore
                pass

        except Exception as e:
            self.config(cursor="")
            self.btn_generate.config(state="normal")
            messagebox.showerror(
                "Resume Error",
                f"Failed to generate resume:\n{e}",
                parent=self,
            )
            return

        # Restore cursor and re-enable button (if user wants to generate again)
        self.config(cursor="")
        self.btn_generate.config(state="normal")
