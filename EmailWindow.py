# EmailWindow.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any
from urllib.parse import quote
from pathlib import Path

import email_service



class EmailWindow(tk.Toplevel):
    def __init__(self, parent, controller, hunt_id: str, context: Dict[str, Any]):
        super().__init__(parent)
        self.controller = controller
        self.hunt_id = hunt_id

        # context: {"personal": {...}, "hunt": {...}, "company": {...}}
        self.context = context

        # Keep track of attachments (list of file paths)
        self.attachments = []


        self.title("Compose Application Email")
        self.geometry("900x700")
        self.iconbitmap("icon.ico")

        # ======================================================
        # Layout structure:
        #   row 0: Context (read-only)
        #   row 1: Preferences
        #   row 2: Email (To / Subject / Body)
        #   row 3: Buttons (Generate / Send-direct / Send-mail-app / Copy)
        # ======================================================
        main = tk.Frame(self)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        main.rowconfigure(0, weight=1)
        main.rowconfigure(1, weight=0)
        main.rowconfigure(2, weight=2)
        main.rowconfigure(3, weight=0)
        main.columnconfigure(0, weight=1)

        # -----------------------------
        # Top: context summary
        # -----------------------------
        ctx_frame = tk.LabelFrame(main, text="Application Context (read-only)")
        ctx_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))

        self.txt_context = tk.Text(ctx_frame, wrap="word", height=10)
        self.txt_context.pack(fill="both", expand=True)
        self.txt_context.config(state="disabled")

        # -----------------------------
        # Middle: preferences
        # -----------------------------
        pref_frame = tk.LabelFrame(main, text="Email Preferences (optional)")
        pref_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 5))
        pref_frame.columnconfigure(1, weight=1)

        row = 0
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
        self.txt_notes = tk.Text(pref_frame, height=3)
        self.txt_notes.grid(row=row, column=1, sticky="nsew", pady=3)
        row += 1

        # -----------------------------
        # Email fields
        # -----------------------------
        email_frame = tk.LabelFrame(main, text="Email")
        email_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 5))
        email_frame.columnconfigure(1, weight=1)
        email_frame.rowconfigure(2, weight=1)  # body grows

        row_e = 0
        tk.Label(email_frame, text="To").grid(row=row_e, column=0, sticky="w", pady=3)
        self.ent_to = tk.Entry(email_frame)
        self.ent_to.grid(row=row_e, column=1, sticky="we", pady=3)
        row_e += 1

        tk.Label(email_frame, text="Subject").grid(row=row_e, column=0, sticky="w", pady=3)
        self.ent_subject = tk.Entry(email_frame)
        self.ent_subject.grid(row=row_e, column=1, sticky="we", pady=3)
        row_e += 1

        tk.Label(email_frame, text="Body").grid(row=row_e, column=0, sticky="nw", pady=3)
        self.txt_body = tk.Text(email_frame, wrap="word")
        self.txt_body.grid(row=row_e, column=1, sticky="nsew", pady=3)

        # -----------------------------
        # Bottom: buttons
        # -----------------------------
        btn_row = tk.Frame(main)
        btn_row.grid(row=3, column=0, sticky="e")

        # Left side: attachment info + button
        self.lbl_attachments = tk.Label(btn_row, text="No attachments")
        self.lbl_attachments.pack(side="left", padx=(0, 10))

        self.btn_attach = tk.Button(
            btn_row,
            text="Attach file(s)...",
            command=self._on_attach_files,
        )
        self.btn_attach.pack(side="left", padx=(0, 10))

        # Right side: main actions (right-to-left)
        self.btn_generate = tk.Button(
            btn_row,
            text="Generate Email",
            command=self._on_generate_clicked,
        )
        self.btn_generate.pack(side="right", padx=(5, 0))

        self.btn_send_direct = tk.Button(
            btn_row,
            text="Send (direct via Gmail)",
            command=self._on_send_direct_clicked,
        )
        self.btn_send_direct.pack(side="right", padx=(5, 0))

        self.btn_send = tk.Button(
            btn_row,
            text="Send (open mail app)",
            command=self._on_send_clicked,
        )
        self.btn_send.pack(side="right", padx=(5, 0))

        self.btn_copy = tk.Button(
            btn_row,
            text="Copy Body",
            command=self._on_copy_body,
        )
        self.btn_copy.pack(side="right")


        # X button just closes
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        # Fill context + default subject
        self._populate_summary()
        self._prefill_subject()

    # =========================================================
    # Context summary
    # =========================================================
    def _populate_summary(self):
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

    def _prefill_subject(self):
        """Best-effort default subject from job title + company."""
        hunt    = self.context.get("hunt", {}) or {}
        company = self.context.get("company", {}) or {}

        job_title = (hunt.get("jobTitle") or "").strip()
        company_name = (company.get("name") or "").strip()

        if not self.ent_subject.get().strip():
            if job_title and company_name:
                self.ent_subject.insert(0, f"Application for {job_title} at {company_name}")
            elif job_title:
                self.ent_subject.insert(0, f"Application for {job_title}")
            else:
                self.ent_subject.insert(0, "Job Application")

    # =========================================================
    # Helpers
    # =========================================================
    def _collect_prefs(self) -> Dict[str, Any]:
        return {
            "tone": self.ent_tone.get().strip(),
            "skillsToEmphasise": self.ent_skills.get().strip(),
            "notes": self.txt_notes.get("1.0", "end").strip(),
        }

    def _auto_fill_to_from_context(self):
        """
        Best-effort: pick company email if available; otherwise fall back
        to personal email. Only fills if 'To' is currently empty.
        """
        if self.ent_to.get().strip():
            return  # user already typed something

        company = self.context.get("company", {}) or {}
        personal = self.context.get("personal", {}) or {}

        candidates = [
            company.get("email", ""),
            company.get("companyEmail", ""),
            company.get("hrEmail", ""),
            personal.get("email", ""),
        ]

        for cand in candidates:
            cand = (cand or "").strip()
            if cand:
                self.ent_to.insert(0, cand)
                break

    # =========================================================
    # Button handlers
    # =========================================================
    def _on_generate_clicked(self):
        """Call AI to generate subject + body into the lower fields."""
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

            email_json = email_service.generate_application_email(context)

            subject = email_json.get("subject", "").strip()
            body = email_json.get("body", "").strip()

            if subject:
                self.ent_subject.delete(0, "end")
                self.ent_subject.insert(0, subject)

            if body:
                self.txt_body.delete("1.0", "end")
                self.txt_body.insert("1.0", body)

            # After generating text, auto-fill To from company/personal
            self._auto_fill_to_from_context()

        except Exception as e:
            self.config(cursor="")
            self.btn_generate.config(state="normal")
            messagebox.showerror(
                "Email Error",
                f"Failed to generate email:\n{e}",
                parent=self,
            )
            return

        self.config(cursor="")
        self.btn_generate.config(state="normal")

    def _on_send_clicked(self):
        """
        Open the default mail client using a mailto: URL,
        passing To / Subject / Body.
        """
        to = self.ent_to.get().strip()
        subject = self.ent_subject.get().strip()
        body = self.txt_body.get("1.0", "end").strip()

        if not to:
            messagebox.showwarning(
                "Missing recipient",
                "Please fill in the 'To' email address before sending.",
                parent=self,
            )
            return

        mailto = f"mailto:{quote(to)}"
        params = []
        if subject:
            params.append("subject=" + quote(subject))
        if body:
            params.append("body=" + quote(body))

        if params:
            mailto += "?" + "&".join(params)

        try:
            import webbrowser
            webbrowser.open(mailto)
        except Exception as e:
            messagebox.showerror(
                "Send Email",
                f"Could not open the default email client:\n{e}",
                parent=self,
            )




    def _on_send_direct_clicked(self):
        """
        Send email directly via Gmail API (no manual mail client).
        First time: browser opens for login + consent.
        Later: uses stored token silently.
        """
        to = self.ent_to.get().strip()
        subject = self.ent_subject.get().strip()
        body = self.txt_body.get("1.0", "end").strip()

        if not to:
            messagebox.showwarning(
                "Missing recipient",
                "Please fill in the 'To' email address before sending.",
                parent=self,
            )
            return

        if not subject or not body:
            if not messagebox.askyesno(
                "Send Email",
                "Subject or body is empty. Send anyway?",
                parent=self,
            ):
                return

        self.btn_send_direct.config(state="disabled")
        self.config(cursor="watch")
        self.update_idletasks()

        try:
            # Now send with attachments (if any)
            msg_info = email_service.send_direct_email(
                to=to,
                subject=subject,
                body=body,
                attachments=self.attachments,
            )
        except Exception as e:
            self.config(cursor="")
            self.btn_send_direct.config(state="normal")
            messagebox.showerror(
                "Send Email",
                f"Failed to send via Gmail:\n{e}",
                parent=self,
            )
            return

        self.config(cursor="")
        self.btn_send_direct.config(state="normal")

        # msg_info is the dict returned by Gmail API; typically has 'id'
        msg_id = msg_info.get("id", "(unknown)")
        messagebox.showinfo(
            "Send Email",
            f"Email sent via Gmail API.\nMessage ID: {msg_id}",
            parent=self,
        )










    def _on_copy_body(self):
        """Copy the current body text to clipboard."""
        body = self.txt_body.get("1.0", "end").strip()
        if not body:
            messagebox.showinfo(
                "Nothing to copy",
                "Email body is empty.",
                parent=self,
            )
            return

        self.clipboard_clear()
        self.clipboard_append(body)
        self.update_idletasks()

        messagebox.showinfo(
            "Copied",
            "Email body copied to clipboard.",
            parent=self,
        )


    def _on_attach_files(self):
        """
        Let the user choose one or more files to attach.
        We store absolute paths in self.attachments and update the label.
        """
        paths = filedialog.askopenfilenames(
            parent=self,
            title="Select attachment(s)",
        )
        if not paths:
            return

        # Extend attachment list; avoid duplicates while preserving order
        for p in paths:
            if p not in self.attachments:
                self.attachments.append(p)

        # Update label with count + a short preview of filenames
        count = len(self.attachments)
        if count == 0:
            text = "No attachments"
        else:
            # Show up to 3 filenames, then "+N more"
            names = [Path(p).name for p in self.attachments[:3]]
            preview = ", ".join(names)
            if count > 3:
                preview += f" (+{count - 3} more)"
            text = f"{count} attachment(s): {preview}"

        self.lbl_attachments.config(text=text)
