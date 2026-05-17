import tkinter as tk


# Κύρια οθόνη μετά το login, με τα κουμπιά για τις διάφορες λειτουργίες
class main_gui:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        master.title("Main")
        master.geometry("1000x650")
        msg=f"Καλώς ήρθατε στην εφαρμογή οικογενειακών οικονομικών {username}!\n\n"

        #Δημιουργια καποιων στοιχείων για testing απο τα gui ΝΑ ΔΙΑΓΡΑΦΟΥΝ ΚΑΤΑ ΤΗΝ ΕΝΩΣΗ ΜΕ DATA BASE
        self.mock_data = [
            {"type": "Έσοδα", "amount": 1000, "category": "Μισθός"},
            {"type": "Έξοδα", "amount": 200, "category": "Φαγητό"},
            {"type": "Έσοδα", "amount": 500, "category": "Επένδυση"},
            {"type": "Έξοδα", "amount": 150, "category": "Μεταφορικά"}
        ]

        # Δημιουργία πλαισίου και κουμπιών

        left_frame = tk.Frame(master)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(left_frame, text="Αρχική", width=35, command=self.show_welcome).pack(pady=5)
        tk.Button(left_frame, text="Εισαγωγή Δεδομένων", width=35, command=self.data_entry).pack(pady=5)
        tk.Button(left_frame, text="Τροποποίηση και Διαγραφή Δεδομένων", width=35, command=self.data_modify).pack(pady=5)
        tk.Button(left_frame, text="Εμφάνιση Δεδομένων", width=35, command=self.data_display).pack(pady=5)
        tk.Button(left_frame, text="Έξοδος", width=35, command=self.exit).pack(pady=5)

        # Δημιουργία text widget για εμφάνιση καλοσορίσματος

        self.right_frame = tk.Frame(master)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
    
        #καλοσορίσμα
        self.show_welcome()

    def clear_right_frame(self):
        for widget in self.right_frame.winfo_children():
            widget.destroy()

    def show_welcome(self):
        self.clear_right_frame()

        center_container = tk.Frame(self.right_frame)
        center_container.pack(expand=True)

        welcome_message = f"Καλώς ήρθατε στην εφαρμογή οικογενειακών οικονομικών {self.username}!\n\nΕπιλέξτε μια λειτουργία από το μενού στα αριστερά για να ξεκινήσετε."
        self.welcome_label = tk.Label(center_container, text=welcome_message, justify=tk.LEFT)
        self.welcome_label.pack(pady=20)

    def data_entry(self):
        self.clear_right_frame()

        center_container = tk.Frame(self.right_frame)
        center_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(center_container, text="Εισαγωγή Δεδομένων", font=("Arial", 16, "bold")).pack(pady=10)

        tk.Label(center_container, text="Επιλέξτε τύπο δεδομένων:").pack()
        choice_frame = tk.Frame(center_container)
        choice_frame.pack(pady=5)
        self.income_button = tk.Button(choice_frame, text="Έσοδα", width=15, command=self.income)
        self.income_button.pack(side=tk.LEFT, padx=5)
        self.expenses_button = tk.Button(choice_frame, text="Έξοδα", width=15, command=self.expenses)
        self.expenses_button.pack(side=tk.RIGHT, padx=5)

        tk.Label(center_container, text="Ποσό:").pack()
        self.entry_amount = tk.Entry(center_container)
        self.entry_amount.pack()

        tk.Label(center_container, text="Κατηγορία:").pack()
        self.entry_category = tk.Entry(center_container)
        self.entry_category.pack()

        tk.Button(center_container, text="Submit", command=self.submit_data).pack(pady=10)
   
    def income(self):
        self.choice = "Έσοδα"
        self.income_button.config(relief=tk.SUNKEN)
        self.expenses_button.config(relief=tk.RAISED)
        print("Επιλέχθηκαν Έσοδα")
    
    def expenses(self):
        self.choice = "Έξοδα"
        self.income_button.config(relief=tk.RAISED)
        self.expenses_button.config(relief=tk.SUNKEN)
        print("Επιλέχθηκαν Έξοδα")
    
    def submit_data(self):
        amount = self.entry_amount.get()
        category = self.entry_category.get()
        data_type = getattr(self, 'data_type', None)
        # Εδώ θα βάλουμε τον τρόπο αποθήκευσης των δεδομένων
        print(f"Amount: {amount}, Category: {category}, Data Type: {data_type}")

    def data_modify(self):
        self.clear_right_frame()
        tk.Label(self.right_frame, text="Τροποποίηση Δεδομένων", font=("Arial", 16, "bold")).pack(pady=10)

        canvas = tk.Canvas(self.right_frame, borderwidth=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.right_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        for record in self.mock_data:
            row = tk.Frame(scrollable_frame, bd=1, relief="solid", padx=5, pady=5)
            row.pack(fill="x", padx=5, pady=5, expand=True)

            info_text=f"Τύπος: {record['type']} | Ποσό: {record['amount']} | Κατηγορία: {record['category']}"
            tk.Label(row, text=info_text, width=50, anchor="w", font=("Arial", 11)).pack(side=tk.LEFT, padx=10)

            tk.Button(row, text="Edit", command=lambda r=record: self.show_edit_gui(r)).pack(side=tk.LEFT, padx=5)
            tk.Button(row, text="Delete", command=lambda r=record: self.delete_record(r)).pack(side=tk.LEFT, padx=5)
        
    def delete_record(self, record):
        print(f"Διαγραφή εγγραφής: {record}")
        # Εδώ θα βάλουμε τον τρόπο διαγραφής των δεδομένων  
        self.mock_data.remove(record)  # ΝΑ ΔΙΑΓΡΑΦΕΙ ΚΑΤΑ ΤΗΝ ΕΝΩΣΗ ΜΕ DATA BASE
        self.data_modify()  # Ενημέρωση της λίστας μετά τη διαγραφή

    def show_edit_gui(self, record):
        self.clear_right_frame()
            
        center_container = tk.Frame(self.right_frame)
        center_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(center_container, text="Τροποποίηση Δεδομένων", font=("Arial", 16, "bold")).pack(pady=10)

        self.choice = record['type']
        tk.Label(center_container, text="Επιλέξτε τύπο δεδομένων:").pack()
        choice_frame = tk.Frame(center_container)
        choice_frame.pack(pady=5)
        self.income_button = tk.Button(choice_frame, text="Έσοδα", width=15, command=self.income)
        self.income_button.pack(side=tk.LEFT, padx=5)
        self.expenses_button = tk.Button(choice_frame, text="Έξοδα", width=15, command=self.expenses)
        self.expenses_button.pack(side=tk.RIGHT, padx=5)
        if self.choice == "Έσοδα":
            self.income()
        else:
            self.expenses()
        tk.Label(center_container, text="Ποσό:").pack()
        self.entry_amount = tk.Entry(center_container)
        self.entry_amount.insert(0, record['amount'])
        self.entry_amount.pack()

        self.entry_category = tk.Entry(center_container)
        self.entry_category.insert(0, record['category'])   
        tk.Label(center_container, text="Κατηγορία:").pack()
        self.entry_category.pack()

        btn_frame = tk.Frame(center_container)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Submit", command=lambda: self.submit_edit(record)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.data_modify).pack(side=tk.RIGHT, padx=5)

    def submit_edit(self, record):
        # Εδώ θα βάλουμε τον τρόπο υποβολής των επεξεργασμένων δεδομένων
        new_amount = self.entry_amount.get()
        new_category = self.entry_category.get()
        new_type = self.choice
        record['amount'] = new_amount  # ΝΑ ΕΝΗΜΕΡΩΝΕΤΑΙ ΚΑΤΑ ΤΗΝ ΕΝΩΣΗ ΜΕ DATA BASE
        record['category'] = new_category  # ΝΑ ΕΝΗΜΕΡΩΝΕΤΑΙ ΚΑΤΑ ΤΗΝ ΕΝΩΣΗ ΜΕ DATA BASE
        record['type'] = new_type  # ΝΑ ΕΝΗΜΕΡΩΝΕΤΑΙ ΚΑΤΑ ΤΗΝ ΕΝΩΣΗ ΜΕ DATA BASE
        print(f"Ενημέρωση εγγραφής: {record} -> Νέο Ποσό: {new_amount}, Νέα Κατηγορία: {new_category}, Τύπος: {self.choice}")
        self.data_modify()  # Ενημέρωση της λίστας μετά την επεξεργασία


    def data_display(self):
        self.clear_right_frame()

        tk.Label(self.right_frame, text="Στατιστικά και Γραφικές Παραστάσεις", font=("Arial", 16, "bold")).pack(pady=10)

        selector_frame = tk.Frame(self.right_frame)
        selector_frame.pack(pady=10)

        tk.Button(selector_frame, text="Έσοδα vs Έξοδα", width=20, command=self.placeholder_chart_1).pack(side=tk.LEFT, padx=5)
        tk.Button(selector_frame, text="Έξοδα ανά κατηγορία", width=20, command=self.placeholder_chart_2).pack(side=tk.LEFT, padx=5)
        tk.Button(selector_frame, text="Μηνιαία Εξέληξη", width=20, command=self.placeholder_chart_3).pack(side=tk.LEFT, padx=5)

        self.chart_container = tk.Frame(self.right_frame)
        self.chart_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.placeholder_chart_1()

    def clear_chart_container(self):
        for widget in self.chart_container.winfo_children():
            widget.destroy()
    
    def placeholder_chart_1(self):
        self.clear_chart_container()
        tk.Label(self.chart_container, text="Γράφημα: Έσοδα vs Έξοδα", font=("Arial", 14)).pack(pady=20)
        # Εδώ θα βάλουμε τον τρόπο εμφάνισης του γραφήματος Έσοδα vs Έξοδα
        # θα πρέπει να χρησιμοποιηθεί το self.chart_container ως master για το γράφημα ώστε να εμφανίζεται στο σωστό σημείο

    def placeholder_chart_2(self):
        self.clear_chart_container()
        tk.Label(self.chart_container, text="Γράφημα: Έξοδα ανά κατηγορία", font=("Arial", 14)).pack(pady=20)
        # Εδώ θα βάλουμε τον τρόπο εμφάνισης του γραφήματος Έξοδα ανά κατηγορία
        # θα πρέπει να χρησιμοποιηθεί το self.chart_container ως master για το γράφημα ώστε να εμφανίζεται στο σωστό σημείο

    def placeholder_chart_3(self):
        self.clear_chart_container()
        tk.Label(self.chart_container, text="Γράφημα: Μηνιαία Εξέλιξη", font=("Arial", 14)).pack(pady=20)
        # Εδώ θα βάλουμε τον τρόπο εμφάνισης του γραφήματος Μηνιαία Εξέλιξη
        # θα πρέπει να χρησιμοποιηθεί το self.chart_container ως master για το γράφημα ώστε να εμφανίζεται στο σωστό σημείο 

    
    def exit(self):
        self.master.destroy()


#Δημιουργία GUI για login
class login_gui:
    def __init__(self, master):
        self.master = master
        master.title("Login")
        master.geometry("300x200")

        self.label = tk.Label(master, text="Παρακαλώ εισάγετε τα στοιχεία σας για σύνδεση:")
        self.label.pack(pady=10)

        self.label_username = tk.Label(master, text="Username")
        self.label_username.pack()

        self.entry_username = tk.Entry(master)
        self.entry_username.pack()

        self.label_password = tk.Label(master, text="Password")
        self.label_password.pack()

        self.entry_password = tk.Entry(master, show="*")
        self.entry_password.pack()

        self.login_button = tk.Button(master, text="Login", command=self.login)
        self.login_button.pack()

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        # Εδώ θα βάλουμε τρόπο επαλήθεσης των στοιχείων σύνδεσης
        print(f"Username: {username}, Password: {password}")
        main_window = tk.Toplevel(self.master)
        self.app = main_gui(main_window, username)
        self.master.withdraw()  



#Δημιουργία GUI για register
class register_gui:
    def __init__(self, master):
        self.master = master
        master.title("Register")
        master.geometry("500x200")

        self.label = tk.Label(master, text="Παρακαλώ εισάγετε τα στοιχεία σας για εγγραφή:")    
        self.label.pack(pady=10)


        self.label_username = tk.Label(master, text="Username")
        self.label_username.pack()

        self.entry_username = tk.Entry(master)
        self.entry_username.pack()

        self.label_password = tk.Label(master, text="Password")
        self.label_password.pack()

        self.entry_password = tk.Entry(master, show="*")
        self.entry_password.pack()

        self.register_button = tk.Button(master, text="Register", command=self.register)
        self.register_button.pack()

    def register(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        # Εδώ θα βάλουμε τον τρόπο εγγραφής χρηστών
        print(f"Username: {username}, Password: {password}")


#Δημιουργία GUI για αρχική οθόνη
class start_gui:
    def __init__(self, master):
        self.master = master
        master.title("Start")
        master.geometry("500x150")

        self.label = tk.Label(master, text="Kαλώς ήρθατε στην εφαρμογή οικογενειακών οικονομικών!\nΠαρακαλώ επιλέξτε login ή register:")
        self.label.pack(pady=10)

        self.login_button = tk.Button(master, text="Login", command=self.open_login)
        self.login_button.pack()

        self.register_button = tk.Button(master, text="Register", command=self.open_register)
        self.register_button.pack()

    def open_login(self):
        login_window = tk.Toplevel(self.master)
        login_gui(login_window)
        self.master.withdraw() 

    def open_register(self):
        register_window = tk.Toplevel(self.master)
        register_gui(register_window)
        self.master.withdraw()


if __name__ == "__main__":
    root = tk.Tk()
    start_gui(root)
    root.mainloop()