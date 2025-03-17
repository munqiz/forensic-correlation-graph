import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import networkx as nx
import matplotlib.pyplot as plt
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# Database setup
conn = sqlite3.connect("cases.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY,
        username TEXT,
        hostname TEXT,
        staff_id INTEGER,
        email TEXT
    );
""")
conn.commit()

def open_case_manager():
    case_window = tk.Toplevel(root)
    case_window.title("Manage Cases")
    case_window.geometry("600x400")
    
    tree = ttk.Treeview(case_window, columns=("ID", "Username", "Hostname", "Staff ID", "Email"), show='headings')
    tree.heading("ID", text="ID")
    tree.heading("Username", text="Username")
    tree.heading("Hostname", text="Hostname")
    tree.heading("Staff ID", text="Staff ID")
    tree.heading("Email", text="Email")
    tree.pack(expand=True, fill="both")
    
    def load_cases():
        tree.delete(*tree.get_children())
        cursor.execute("SELECT * FROM cases;")
        for case in cursor.fetchall():
            tree.insert("", tk.END, values=case)
    
    def add_case():
        add_window = tk.Toplevel(case_window)
        add_window.title("Add Case")
        
        tk.Label(add_window, text="Username:").grid(row=0, column=0)
        username_entry = tk.Entry(add_window)
        username_entry.grid(row=0, column=1)
        
        tk.Label(add_window, text="Hostname:").grid(row=1, column=0)
        hostname_entry = tk.Entry(add_window)
        hostname_entry.grid(row=1, column=1)
        
        tk.Label(add_window, text="Staff ID:").grid(row=2, column=0)
        staff_id_entry = tk.Entry(add_window)
        staff_id_entry.grid(row=2, column=1)
        
        tk.Label(add_window, text="Email:").grid(row=3, column=0)
        email_entry = tk.Entry(add_window)
        email_entry.grid(row=3, column=1)
        
        def save_case():
            cursor.execute("INSERT INTO cases (username, hostname, staff_id, email) VALUES (?, ?, ?, ?)",
                           (username_entry.get(), hostname_entry.get(), staff_id_entry.get(), email_entry.get()))
            conn.commit()
            load_cases()
            add_window.destroy()
            messagebox.showinfo("Success", "Case added successfully!")
        
        tk.Button(add_window, text="Save", command=save_case).grid(row=4, columnspan=2)
    
    def delete_case():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No case selected.")
            return
        
        case_id = tree.item(selected_item)['values'][0]
        cursor.execute("DELETE FROM cases WHERE id = ?", (case_id,))
        conn.commit()
        load_cases()
        messagebox.showinfo("Success", "Case deleted successfully!")
    
    def edit_case():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No case selected.")
            return
        
        case_data = tree.item(selected_item)['values']
        edit_window = tk.Toplevel(case_window)
        edit_window.title("Edit Case")
        
        tk.Label(edit_window, text="Username:").grid(row=0, column=0)
        username_entry = tk.Entry(edit_window)
        username_entry.insert(0, case_data[1])
        username_entry.grid(row=0, column=1)
        
        tk.Label(edit_window, text="Hostname:").grid(row=1, column=0)
        hostname_entry = tk.Entry(edit_window)
        hostname_entry.insert(0, case_data[2])
        hostname_entry.grid(row=1, column=1)
        
        tk.Label(edit_window, text="Staff ID:").grid(row=2, column=0)
        staff_id_entry = tk.Entry(edit_window)
        staff_id_entry.insert(0, case_data[3])
        staff_id_entry.grid(row=2, column=1)
        
        tk.Label(edit_window, text="Email:").grid(row=3, column=0)
        email_entry = tk.Entry(edit_window)
        email_entry.insert(0, case_data[4])
        email_entry.grid(row=3, column=1)
        
        def update_case():
            cursor.execute("UPDATE cases SET username=?, hostname=?, staff_id=?, email=? WHERE id=?", 
                           (username_entry.get(), hostname_entry.get(), staff_id_entry.get(), email_entry.get(), case_data[0]))
            conn.commit()
            load_cases()
            edit_window.destroy()
            messagebox.showinfo("Success", "Case updated successfully!")
        
        tk.Button(edit_window, text="Update", command=update_case).grid(row=4, columnspan=2)
    
    def view_graph():
        cursor.execute("SELECT * FROM cases;")
        cases = cursor.fetchall()
        df = pd.DataFrame(cases, columns=["id", "username", "hostname", "staff_id", "email"])
        
        G = nx.Graph()
        for i in range(len(df)):
            for j in range(i+1, len(df)):
                if (df.iloc[i][1] == df.iloc[j][1] or
                    df.iloc[i][2] == df.iloc[j][2] or
                    df.iloc[i][3] == df.iloc[j][3] or
                    df.iloc[i][4] == df.iloc[j][4]):
                    G.add_edge(str(df.iloc[i][0]), str(df.iloc[j][0]))
        
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True)
        plt.show()
    
    btn_frame = tk.Frame(case_window)
    btn_frame.pack()
    tk.Button(btn_frame, text="Add Case", command=add_case).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Edit Case", command=edit_case).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Delete Case", command=delete_case).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="View Graph", command=view_graph).pack(side=tk.LEFT, padx=5)
    load_cases()

# Main GUI setup
root = tk.Tk()
root.title("Case Management System")
root.geometry("500x400")

tk.Button(root, text="Manage Cases", command=open_case_manager, width=20, bg="#4CAF50", fg="white").pack(pady=10)
tk.Button(root, text="Exit", command=root.quit, width=20, bg="#F44336", fg="white").pack(pady=10)

root.mainloop()
conn.close()
