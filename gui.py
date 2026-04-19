from doctest import master
import tkinter as tk


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
        tk.Button(left_frame, text="Εισαγωγή Δεδομένων", width=35, command=self.b1_pushed).pack(pady=5)
        tk.Button(left_frame, text="Τροποποίηση Δεδομένων", width=35, command=self.b2_pushed).pack(pady=5)
        tk.Button(left_frame, text="Διαγραφή Δεδομένων", width=35, command=self.b3_pushed).pack(pady=5)
        tk.Button(left_frame, text="Εμφάνιση Δεδομένων", width=35, command=self.b4_pushed).pack(pady=5)
        tk.Button(left_frame, text="Έξοδος", width=35, command=self.b5_pushed).pack(pady=5)

        # Δημιουργία text widget για εμφάνιση καλοσορίσματος

        right_frame = tk.Frame(master)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.output_text = tk.Text(right_frame, width=60, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, msg)
    
    def b1_pushed(self):
        pass
    
    def b2_pushed(self):
        pass
    
    def b3_pushed(self):
        pass
    
    def b4_pushed(self):
        pass
    
    def b5_pushed(self):
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