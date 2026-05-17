from doctest import master
import tkinter as tk


# Κύρια οθόνη μετά το login, με τα κουμπιά για τις διάφορες λειτουργίες
class main_gui:
    def __init__(self, master, username):
        self.master = master
        self.username = username
        master.title("Main")
        master.geometry("850x650")
        msg=f"Καλώς ήρθατε στην εφαρμογή οικογενειακών οικονομικών {username}!\n\n"

        # Δημιουργία πλαισίου και κουμπιών

        left_frame = tk.Frame(master)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(left_frame, text="Αρχική", width=35, command=self.show_welcome).pack(pady=5)
        tk.Button(left_frame, text="Εισαγωγή Δεδομένων", width=35, command=self.data_entry).pack(pady=5)
        tk.Button(left_frame, text="Τροποποίηση Δεδομένων", width=35, command=self.data_modify).pack(pady=5)
        tk.Button(left_frame, text="Διαγραφή Δεδομένων", width=35, command=self.data_delete).pack(pady=5)
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
        pass

    def data_delete(self):
        pass

    def data_display(self):
        pass
    
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