import tkinter as tk
import webbrowser
from datetime import date, timedelta
from tkinter import messagebox, ttk

from auth import authenticate, register_patient
from database import appointments, doctors, learning_resources, medical_records, payments, patients, prescriptions, reports, users
from validation import normalize_value


ENTITY_MODULES = {
    "Patients": patients.repository,
    "Doctors": doctors.repository,
    "Appointments": appointments.repository,
    "Medical records": medical_records.repository,
    "Prescriptions": prescriptions.repository,
    "Payments": payments.repository,
    "Learning resources": learning_resources.repository,
}

ROLE_TABS = {
    "administrator": ("Patients", "Doctors", "Appointments", "Medical records", "Prescriptions", "Payments", "Learning resources", "Reports"),
    "doctor": ("Patients", "Appointments", "Medical records", "Prescriptions", "Learning resources", "Reports"),
    "receptionist": ("Patients", "Doctors", "Appointments", "Payments", "Learning resources", "Reports"),
    "patient": ("Appointments", "Medical records", "Learning resources"),
}

PATIENT_HEADERS = {
    "Appointments": (("appointment_id", "ID"), ("doctor", "Doctor"), ("appointment_date", "Date"),
                     ("appointment_time", "Time"), ("status", "Status"), ("reason", "Reason")),
    "Medical records": (("medical_record_id", "ID"), ("appointment_id", "Appointment"),
                        ("doctor", "Doctor"), ("medical_history", "Medical history"),
                        ("diagnosis", "Diagnosis"), ("notes", "Notes"), ("created_at", "Recorded")),
}


class LoginWindow:
    def __init__(self, root, on_login):
        self.root = root
        self.on_login = on_login
        self.window = tk.Toplevel(root)
        self.window.title("St. Lucy | Sign in")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", root.destroy)
        self.window.transient(root)
        self.window.grab_set()
        self.window.geometry("420x330")

        panel = ttk.Frame(self.window, padding=30)
        panel.pack(fill="both", expand=True)
        ttk.Label(panel, text="ST. LUCY CLINIC", font=("Helvetica", 11, "bold")).pack(anchor="w")
        ttk.Label(panel, text="Patient management", font=("Helvetica", 23, "bold")).pack(anchor="w", pady=(6, 22))
        ttk.Label(panel, text="Username").pack(anchor="w")
        self.username = ttk.Entry(panel, width=40)
        self.username.pack(fill="x", pady=(4, 12))
        ttk.Label(panel, text="Password").pack(anchor="w")
        self.password = ttk.Entry(panel, width=40, show="*")
        self.password.pack(fill="x", pady=(4, 18))
        actions = ttk.Frame(panel)
        actions.pack(fill="x")
        ttk.Button(actions, text="Sign in", command=self.sign_in).pack(side="left")
        ttk.Button(actions, text="Patient registration", command=self.register).pack(side="right")
        self.window.bind("<Return>", lambda _event: self.sign_in())
        self.username.focus_set()

    def sign_in(self):
        try:
            user = authenticate(self.username.get(), self.password.get())
        except Exception as exc:
            messagebox.showerror("Connection failed", f"Could not sign in. Check PostgreSQL and .env.\n\n{exc}", parent=self.window)
            return
        if not user:
            messagebox.showerror("Sign-in failed", "The username or password is incorrect, or the account is inactive.", parent=self.window)
            return
        self.window.grab_release()
        self.window.destroy()
        self.on_login(user)

    def register(self):
        PatientRegistration(self.window)


class PatientRegistration:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Patient registration")
        self.window.transient(parent)
        self.window.grab_set()
        self.fields = {}
        form = ttk.Frame(self.window, padding=20)
        form.pack(fill="both", expand=True)
        rows = (
            ("full_name", "Full name"), ("date_of_birth", "Date of birth (YYYY-MM-DD)"),
            ("gender", "Gender"), ("phone_number", "Phone number"), ("email", "Email"),
            ("username", "Username"), ("password", "Password (10+ characters)"),
        )
        for row, (key, label) in enumerate(rows):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=5)
            if key == "gender":
                widget = ttk.Combobox(form, values=("Female", "Male", "Other", "Prefer not to say"), state="readonly")
            else:
                widget = ttk.Entry(form, show="*" if key == "password" else "")
            widget.grid(row=row, column=1, sticky="ew", pady=5)
            self.fields[key] = widget
        form.columnconfigure(1, weight=1)
        ttk.Button(form, text="Create patient account", command=self.save).grid(row=len(rows), column=1, sticky="e", pady=(14, 0))

    def save(self):
        try:
            values = {key: widget.get().strip() for key, widget in self.fields.items()}
            birth_date = normalize_value("date", values["date_of_birth"], "Date of birth", True)
            register_patient(values["username"], values["password"], values["full_name"], birth_date,
                             values["gender"], values["phone_number"], values["email"])
        except Exception as exc:
            messagebox.showerror("Registration failed", str(exc), parent=self.window)
            return
        messagebox.showinfo("Account created", "Your patient account is ready. Sign in to view your appointments, records, and learning resources.", parent=self.window)
        self.window.destroy()


class MainApplication:
    def __init__(self, root, user):
        self.root = root
        self.user = user
        self.frame = ttk.Frame(root)
        self.frame.pack(fill="both", expand=True)
        self.root.deiconify()
        self.root.title("St. Lucy Clinic | Patient Management")
        self.root.geometry("1180x760")
        self.root.minsize(900, 600)

        top = ttk.Frame(self.frame, padding=(18, 14))
        top.pack(fill="x")
        ttk.Label(top, text="ST. LUCY CLINIC", font=("Helvetica", 11, "bold")).pack(side="left")
        ttk.Label(top, text=f"{user['username']}  ·  {user['role'].title()}").pack(side="right", padx=(12, 0))
        if user["role"] == "administrator":
            ttk.Button(top, text="User accounts", command=self.manage_users).pack(side="right")
        ttk.Button(top, text="Sign out", command=self.sign_out).pack(side="right", padx=10)

        self.tabs = ttk.Notebook(self.frame)
        self.tabs.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        if user["role"] != "patient":
            self.tabs.add(DashboardPage(self.tabs), text="Overview")
        for title in ROLE_TABS[user["role"]]:
            if title == "Reports":
                page = ReportsPage(self.tabs)
            else:
                page = EntityPage(self.tabs, title, ENTITY_MODULES[title], user)
            self.tabs.add(page, text=title)

    def manage_users(self):
        UserManagement(self.root, self.user["user_id"])

    def sign_out(self):
        self.frame.destroy()
        self.root.withdraw()
        LoginWindow(self.root, lambda user: MainApplication(self.root, user))


class DashboardPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        ttk.Label(self, text="Clinic overview", font=("Helvetica", 18, "bold")).pack(anchor="w")
        ttk.Label(self, text="Live counts from the clinic database").pack(anchor="w", pady=(2, 18))
        self.values = {}
        cards = ttk.Frame(self)
        cards.pack(fill="x")
        for key, title in (("patients", "Patients"), ("active_doctors", "Active doctors"),
                           ("upcoming_appointments", "Upcoming appointments"), ("revenue_today", "Today's revenue (UGX)")):
            card = ttk.LabelFrame(cards, text=title, padding=16)
            card.pack(side="left", fill="both", expand=True, padx=(0, 10))
            self.values[key] = ttk.Label(card, text="--", font=("Helvetica", 20, "bold"))
            self.values[key].pack(anchor="w")
        ttk.Button(self, text="Refresh", command=self.refresh).pack(anchor="w", pady=20)
        self.after(100, self.refresh)

    def refresh(self):
        try:
            summary = reports.dashboard_summary()
            for key, label in self.values.items():
                value = summary[key]
                label.configure(text=f"{value:,.0f}" if key == "revenue_today" else str(value))
        except Exception as exc:
            messagebox.showerror("Database error", str(exc), parent=self)


class EntityPage(ttk.Frame):
    def __init__(self, parent, title, repository, user):
        super().__init__(parent, padding=14)
        self.title = title
        self.repository = repository
        self.user = user
        self.read_only = user["role"] == "patient" or (title == "Learning resources" and user["role"] != "administrator")
        self.columns = PATIENT_HEADERS.get(title, repository.headers) if user["role"] == "patient" else repository.headers

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 10))
        ttk.Label(toolbar, text=title, font=("Helvetica", 17, "bold")).pack(side="left")
        if title == "Learning resources":
            ttk.Button(toolbar, text="Open selected resource", command=self.open_selected).pack(side="right", padx=(8, 0))
        if not self.read_only:
            ttk.Button(toolbar, text="Add", command=self.add).pack(side="right", padx=(8, 0))
            ttk.Button(toolbar, text="Edit selected", command=self.edit).pack(side="right", padx=(8, 0))
        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(side="right")

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)
        keys = [key for key, _label in self.columns]
        self.tree = ttk.Treeview(body, columns=keys, show="headings", selectmode="browse")
        for key, label in self.columns:
            self.tree.heading(key, text=label)
            self.tree.column(key, width=140, minwidth=80, stretch=True)
        yscroll = ttk.Scrollbar(body, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(body, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)
        self.tree.bind("<Double-1>", lambda _event: self.open_selected() if title == "Learning resources" else None)
        self.after(100, self.refresh)

    def refresh(self):
        try:
            if self.user["role"] == "patient" and self.title in PATIENT_HEADERS:
                rows = self.repository.list_for_patient(self.user["patient_id"])
            elif self.title == "Learning resources" and self.user["role"] != "administrator":
                rows = self.repository.list_public()
            else:
                rows = self.repository.list_all()
            self.tree.delete(*self.tree.get_children())
            for row in rows:
                values = [row.get(key, "") for key, _label in self.columns]
                self.tree.insert("", "end", iid=str(row[self.columns[0][0]]), values=values)
        except Exception as exc:
            messagebox.showerror("Database error", str(exc), parent=self)

    def selected_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Select a row", "Choose a record first.", parent=self)
            return None
        return selection[0]

    def add(self):
        FormDialog(self, self.title, self.repository, self.user, None, self.refresh)

    def edit(self):
        record_id = self.selected_id()
        if record_id:
            FormDialog(self, self.title, self.repository, self.user, record_id, self.refresh)

    def open_selected(self):
        record_id = self.selected_id()
        if not record_id:
            return
        try:
            row = self.repository.get(record_id)
            if row and row.get("active"):
                webbrowser.open(row["url"])
            elif row:
                messagebox.showinfo("Resource unavailable", "This resource is currently inactive.", parent=self)
        except Exception as exc:
            messagebox.showerror("Could not open resource", str(exc), parent=self)


class FormDialog:
    def __init__(self, parent, title, repository, user, record_id, on_saved):
        self.repository = repository
        self.user = user
        self.record_id = record_id
        self.on_saved = on_saved
        self.window = tk.Toplevel(parent)
        self.window.title(f"{'Edit' if record_id else 'Add'} {title.rstrip('s')}")
        self.window.transient(parent)
        self.window.grab_set()
        self.window.geometry("620x560")
        self.fields = {}
        self.choice_maps = {}
        current = repository.get(record_id) if record_id else {}
        form = ttk.Frame(self.window, padding=20)
        form.pack(fill="both", expand=True)
        form.columnconfigure(1, weight=1)

        for row, (key, label, required, kind) in enumerate(repository.form_fields):
            ttk.Label(form, text=label + (" *" if required else "")).grid(row=row, column=0, sticky="nw", padx=(0, 14), pady=6)
            if kind == "lookup":
                options = repository.choices(key)
                id_key, label_key = repository.lookups[key][1:]
                mapping = {f"{item[id_key]} - {item[label_key]}": item[id_key] for item in options}
                widget = ttk.Combobox(form, values=tuple(mapping), state="readonly")
                self.choice_maps[key] = mapping
                existing = current.get(key)
                if existing is not None:
                    for display, option_id in mapping.items():
                        if str(option_id) == str(existing):
                            widget.set(display)
                            break
            elif kind == "choice":
                widget = ttk.Combobox(form, values=repository.options.get(key, ()), state="readonly")
                if current.get(key) is not None:
                    widget.set(str(current[key]))
            elif kind == "boolean":
                widget = ttk.Combobox(form, values=("Yes", "No"), state="readonly")
                widget.set("Yes" if current.get(key, True) else "No")
            elif kind == "multiline":
                widget = tk.Text(form, height=4, wrap="word")
                if current.get(key):
                    widget.insert("1.0", str(current[key]))
            else:
                widget = ttk.Entry(form)
                if current.get(key) is not None:
                    widget.insert(0, str(current[key]))
            widget.grid(row=row, column=1, sticky="ew", pady=6)
            self.fields[key] = (widget, label, required, kind)

        buttons = ttk.Frame(form)
        buttons.grid(row=len(repository.form_fields), column=1, sticky="e", pady=(14, 0))
        ttk.Button(buttons, text="Cancel", command=self.window.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(buttons, text="Save", command=self.save).pack(side="right")

    def save(self):
        try:
            values = {}
            for key, (widget, label, required, kind) in self.fields.items():
                if kind == "multiline":
                    raw = widget.get("1.0", "end-1c").strip()
                elif kind == "boolean":
                    raw = widget.get() == "Yes"
                elif kind == "lookup":
                    raw = self.choice_maps[key].get(widget.get())
                    if raw is not None:
                        raw = int(raw)
                else:
                    raw = widget.get().strip()
                if kind in ("choice", "boolean", "lookup", "multiline"):
                    if required and (raw is None or raw == ""):
                        raise ValueError(f"{label} is required.")
                    values[key] = raw if raw != "" else None
                else:
                    values[key] = normalize_value(kind, raw, label, required)
            if self.record_id:
                self.repository.update(self.record_id, values)
            else:
                self.repository.create(values, self.user["user_id"])
        except Exception as exc:
            messagebox.showerror("Could not save", str(exc), parent=self.window)
            return
        self.window.destroy()
        self.on_saved()


class UserManagement:
    def __init__(self, parent, current_user_id):
        self.current_user_id = current_user_id
        self.window = tk.Toplevel(parent)
        self.window.title("Staff user accounts")
        self.window.geometry("650x430")
        self.tree = ttk.Treeview(self.window, columns=("user_id", "username", "role", "active"), show="headings")
        for key, label in (("user_id", "ID"), ("username", "Username"), ("role", "Role"), ("active", "Active")):
            self.tree.heading(key, text=label)
            self.tree.column(key, width=140)
        self.tree.pack(fill="both", expand=True, padx=14, pady=14)
        toolbar = ttk.Frame(self.window, padding=(14, 0, 14, 14))
        toolbar.pack(fill="x")
        ttk.Button(toolbar, text="Create staff account", command=self.create).pack(side="left")
        ttk.Button(toolbar, text="Toggle active", command=self.toggle).pack(side="left", padx=8)
        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(side="right")
        self.refresh()

    def refresh(self):
        try:
            self.tree.delete(*self.tree.get_children())
            for row in users.list_all():
                self.tree.insert("", "end", iid=str(row["user_id"]),
                                 values=(row["user_id"], row["username"], row["role"], row["active"]))
        except Exception as exc:
            messagebox.showerror("Database error", str(exc), parent=self.window)

    def create(self):
        StaffAccountDialog(self.window, self.refresh)

    def toggle(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select a user", "Choose an account first.", parent=self.window)
            return
        user_id = int(selected[0])
        if user_id == self.current_user_id:
            messagebox.showwarning("Current account", "You cannot disable the account currently in use.", parent=self.window)
            return
        current = self.tree.item(selected[0], "values")[3]
        try:
            users.set_active(user_id, str(current).lower() not in ("true", "1"))
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Could not update account", str(exc), parent=self.window)


class StaffAccountDialog:
    def __init__(self, parent, on_saved):
        self.on_saved = on_saved
        self.window = tk.Toplevel(parent)
        self.window.title("Create staff account")
        self.window.transient(parent)
        self.window.grab_set()
        form = ttk.Frame(self.window, padding=20)
        form.pack(fill="both", expand=True)
        self.username = ttk.Entry(form)
        self.password = ttk.Entry(form, show="*")
        self.role = ttk.Combobox(form, values=("administrator", "doctor", "receptionist"), state="readonly")
        self.role.set("receptionist")
        for row, (label, widget) in enumerate((("Username", self.username), ("Password (10+ characters)", self.password), ("Role", self.role))):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=6)
            widget.grid(row=row, column=1, sticky="ew", pady=6)
        form.columnconfigure(1, weight=1)
        ttk.Button(form, text="Create", command=self.save).grid(row=3, column=1, sticky="e", pady=(12, 0))

    def save(self):
        try:
            users.add_staff(self.username.get(), self.password.get(), self.role.get())
        except Exception as exc:
            messagebox.showerror("Could not create account", str(exc), parent=self.window)
            return
        self.window.destroy()
        self.on_saved()


class ReportsPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=14)
        ttk.Label(self, text="Clinic reports", font=("Helvetica", 17, "bold")).pack(anchor="w")
        filters = ttk.Frame(self)
        filters.pack(fill="x", pady=10)
        self.start = ttk.Entry(filters, width=14)
        self.end = ttk.Entry(filters, width=14)
        self.start.insert(0, (date.today() - timedelta(days=30)).isoformat())
        self.end.insert(0, date.today().isoformat())
        ttk.Label(filters, text="From (YYYY-MM-DD)").pack(side="left")
        self.start.pack(side="left", padx=(8, 16))
        ttk.Label(filters, text="To").pack(side="left")
        self.end.pack(side="left", padx=8)
        ttk.Button(filters, text="Run appointment report", command=self.refresh_appointments).pack(side="left", padx=12)

        columns = ("appointment_date", "appointment_time", "patient", "doctor", "status", "reason")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        for key, label in zip(columns, ("Date", "Time", "Patient", "Doctor", "Status", "Reason")):
            self.tree.heading(key, text=label)
            self.tree.column(key, width=135)
        self.tree.pack(fill="x", expand=False)

        ttk.Label(self, text="Revenue by month (UGX)", font=("Helvetica", 13, "bold")).pack(anchor="w", pady=(18, 6))
        self.chart = tk.Canvas(self, height=210, background="white", highlightthickness=1, highlightbackground="#d4dadd")
        self.chart.pack(fill="both", expand=True)
        self.chart.bind("<Configure>", lambda _event: self.refresh_chart())
        self.after(150, self.refresh_all)

    def refresh_all(self):
        self.refresh_appointments()
        self.refresh_chart()

    def refresh_appointments(self):
        try:
            start_date = normalize_value("date", self.start.get(), "Start date", True)
            end_date = normalize_value("date", self.end.get(), "End date", True)
            if end_date < start_date:
                raise ValueError("End date must be on or after the start date.")
            rows = reports.appointment_report(start_date, end_date)
            self.tree.delete(*self.tree.get_children())
            for index, row in enumerate(rows):
                self.tree.insert("", "end", iid=str(index), values=tuple(row[key] for key in self.tree["columns"]))
        except Exception as exc:
            messagebox.showerror("Report unavailable", str(exc), parent=self)

    def refresh_chart(self):
        try:
            rows = reports.revenue_by_month()
        except Exception:
            return
        self.chart.delete("all")
        if not rows:
            self.chart.create_text(18, 20, anchor="nw", text="No payment data for the selected period.")
            return
        width = max(self.chart.winfo_width(), 500)
        height = max(self.chart.winfo_height(), 180)
        maximum = max(float(row["total"]) for row in rows) or 1
        band = (width - 45) / len(rows)
        for index, row in enumerate(rows):
            x0 = 25 + index * band + band * 0.2
            x1 = 25 + (index + 1) * band - band * 0.2
            bar_height = (height - 55) * float(row["total"]) / maximum
            y0 = height - 30 - bar_height
            self.chart.create_rectangle(x0, y0, x1, height - 30, fill="#167c80", outline="")
            self.chart.create_text((x0 + x1) / 2, height - 15, text=row["month"].strftime("%b %Y"), font=("Helvetica", 9))
            self.chart.create_text((x0 + x1) / 2, max(10, y0 - 10), text=f"{float(row['total']):,.0f}", font=("Helvetica", 8))


def main():
    root = tk.Tk()
    root.withdraw()
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    style.configure("TNotebook.Tab", padding=(12, 8))
    LoginWindow(root, lambda user: MainApplication(root, user))
    root.mainloop()


if __name__ == "__main__":
    main()
