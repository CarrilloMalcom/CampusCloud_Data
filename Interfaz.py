import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from Campus_cloud_elements.Subject import Subject
from Campus_cloud_elements.Users import User
from Campus_cloud_elements.Material import MaterialTable
from Campus_cloud_elements.DriveSync_OAuth import upload_excel_to_drive, download_excel_from_drive
from Campus_cloud_elements.Subject import Subject
import os
import pandas as pd

class CampusCloudApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CampusCloud")
        self.root.geometry("800x600")
        self.root.configure(bg='#000000')
        self.subjects = []
        self.current_subject = None
        self.configure_styles()
        self.create_main_structure()
        Subject.import_all_from_excel()
        self.load_all_subjects()
        self.show_home_view()

    def load_all_subjects(self):
        folder = "subjects_data"
        if not os.path.exists(folder):
            return
        for file in os.listdir(folder):
            if file.endswith(".txt"):
                try:
                    subject = Subject.load_from_file(os.path.join(folder, file))
                    self.subjects.append(subject)
                    print(f"Materia '{subject.name}' cargada desde archivo.")
                except Exception as e:
                    print(f"Error cargando {file}: {e}")

    def configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background='#111111', foreground='white')
        self.style.configure('Header.TFrame', background='#222222')
        self.style.configure('Header.TLabel', background='#222222', foreground='white', font=('Arial', 24, 'bold'))
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('Save.TButton', background="#231C1C", foreground='white', font=('Arial', 6, 'bold'), borderwidth=2, relief='raised')
        self.style.configure('Cancel.TButton', background="#231C1C", foreground='white', font=('Arial', 6, 'bold'), borderwidth=2, relief='raised')
        self.style.map('Save.TButton', background=[('active', "#000000")])
        self.style.map('Cancel.TButton', background=[('active', "#000000")])
        self.style.configure('TEntry', foreground='white', fieldbackground='#222222', insertbackground='white', bordercolor='#444444', lightcolor='#444444', darkcolor='#444444')

    def create_main_structure(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.create_header()
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        self.create_footer()

    def create_header(self):
        self.header_frame = ttk.Frame(self.main_frame, style='Header.TFrame')
        self.header_frame.pack(fill=tk.X)
        self.title_label = ttk.Label(self.header_frame, text="CampusCloud", style='Header.TLabel', cursor="hand2")
        self.title_label.pack(side=tk.LEFT, padx=20, pady=15)
        self.title_label.bind("<Button-1>", lambda e: self.show_home_view())

    def create_footer(self):
        self.footer_frame = ttk.Frame(self.main_frame)
        self.footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.add_button = tk.Button(self.footer_frame, text="+", font=('Arial', 20), bg="#3E7BC5", fg='white', bd=0, width=3, height=1, command=self.open_add_subject_window)
        self.add_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def open_add_subject_window(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Agregar Nueva Materia")
        add_window.geometry("350x220")
        add_window.configure(bg='#222222')
        add_window.resizable(False, False)
        self.center_window(add_window, 350, 220)

        form_frame = ttk.Frame(add_window, padding=20)
        form_frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(form_frame, text="Nombre de la materia:").pack(anchor='w', pady=(0, 5))
        name_entry = ttk.Entry(form_frame)
        name_entry.pack(fill=tk.X, pady=(0, 15), ipady=5)

        ttk.Label(form_frame, text="Créditos:").pack(anchor='w', pady=(0, 5))
        credits_entry = ttk.Entry(form_frame)
        credits_entry.pack(fill=tk.X, pady=(0, 20), ipady=5)

        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        cancel_btn = ttk.Button(button_frame, text="CANCELAR", style='Cancel.TButton', command=add_window.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=10, ipadx=10, ipady=5)

        save_btn = ttk.Button(button_frame, text="GUARDAR", style='Save.TButton',
                              command=lambda: self.save_new_subject(name_entry.get(), credits_entry.get(), add_window))
        save_btn.pack(side=tk.RIGHT, ipadx=10, ipady=5)

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def save_new_subject(self, name, credits, window):
        if not name or not credits:
            messagebox.showerror("Error", "Debes completar todos los campos")
            return
        try:
            credits = int(credits)
            subject = Subject(name, credits)
            self.subjects.append(subject)
            subject.save_to_file()
            window.destroy()
            self.show_home_view()
        except ValueError:
            messagebox.showerror("Error", "Los créditos deben ser un número entero")

    def show_home_view(self):
        self.clear_content_frame()
        self.current_subject = None
        if not self.subjects:
            welcome_label = ttk.Label(self.content_frame, text="Bienvenido a CampusCloud\n\nHaz clic en el botón + para agregar una materia", font=('Arial', 14), justify='center')
            welcome_label.pack(expand=True, pady=100)
        for subject in self.subjects:
            self.display_subject(subject)

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def display_subject(self, subject):
        subject_frame = ttk.Frame(self.content_frame, style='TFrame', padding=10, relief='groove', borderwidth=2)
        subject_frame.pack(fill=tk.X, pady=5, padx=10)
        info_frame = ttk.Frame(subject_frame)
        info_frame.pack(fill=tk.X)
        ttk.Label(info_frame, text=f"Materia: {subject.name}", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        ttk.Label(info_frame, text=f"Créditos: {subject.credits}", font=('Arial', 12)).pack(side=tk.RIGHT)
        ttk.Button(subject_frame, text="Ver Detalles", command=lambda s=subject: self.show_subject_detail_view(s)).pack(pady=(10, 0))

    def show_subject_detail_view(self, subject):
        self.clear_content_frame()
        self.current_subject = subject
        ttk.Button(self.content_frame, text="Volver", command=self.show_home_view).pack(anchor=tk.W, padx=10, pady=10)

        header_frame = ttk.Frame(self.content_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(header_frame, text=f"Materia: {subject.name}", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        ttk.Label(header_frame, text=f"Créditos: {subject.credits}", font=('Arial', 14)).pack(side=tk.RIGHT)

        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        grades_tab = ttk.Frame(notebook)
        notebook.add(grades_tab, text="Notas")

        def refresh_grades():
            for widget in grades_tab.winfo_children():
                widget.destroy()
            self.create_section_with_add(grades_tab, "Nota", subject.grades)

        refresh_grades()

        assignments_tab = ttk.Frame(notebook)
        notebook.add(assignments_tab, text="Tareas Pendientes")
        self.create_task_section(assignments_tab, subject, refresh_grades)

        materials_tab = ttk.Frame(notebook)
        notebook.add(materials_tab, text="Material de Estudio")
        self.create_section_with_add(materials_tab, "Material", subject.materials)

    def create_task_section(self, frame, subject, refresh_grades=None):
        items_frame = ttk.Frame(frame)
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def refresh_tasks():
            for widget in items_frame.winfo_children():
                widget.destroy()

            for index, task in enumerate(subject.tasks):
                task_frame = ttk.Frame(items_frame)
                task_frame.pack(fill=tk.X, pady=2)

                estado = "✅" if task["Completada"] else "⏳"
                fecha = task["DueDate"].strftime('%Y-%m-%d')
                task_text = f"{estado} {task['Estado']} (Vence: {fecha})"
                ttk.Label(task_frame, text=task_text).pack(side=tk.LEFT, padx=5)

                complete_btn = ttk.Button(task_frame, text="✔", width=3, command=lambda idx=index: complete_task(idx))
                complete_btn.pack(side=tk.RIGHT, padx=2)

                delete_btn = ttk.Button(task_frame, text="✖", width=3, command=lambda idx=index: delete_task(idx))
                delete_btn.pack(side=tk.RIGHT, padx=2)

        def complete_task(index):
            if 0 <= index < len(subject.tasks):
                task = subject.tasks[index]
                subject.Completetasks(index)
                subject.grades.append({"Tarea": task["Estado"], "Nota": ""})
                subject.save_to_file()
                refresh_tasks()
                refresh_grades()

        def delete_task(index):
            if 0 <= index < len(subject.tasks):
                subject.DeleteTask(index)
                subject.save_to_file()
                refresh_tasks()

        refresh_tasks()

        add_frame = ttk.Frame(frame)
        add_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(add_frame, text="Tarea:").pack(side=tk.LEFT)
        task_entry = ttk.Entry(add_frame)
        task_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        ttk.Label(add_frame, text="Fecha (YYYY-MM-DD):").pack(side=tk.LEFT, padx=(10, 0))
        date_entry = ttk.Entry(add_frame, width=12)
        date_entry.pack(side=tk.LEFT, padx=5)

        def add_task():
            text = task_entry.get().strip()
            date_text = date_entry.get().strip()
            if not text or not date_text:
                messagebox.showwarning("Campos vacíos", "Debes ingresar tarea y fecha")
                return
            try:
                subject.addTask(text, date_text)
                task_entry.delete(0, tk.END)
                date_entry.delete(0, tk.END)
                refresh_tasks()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(add_frame, text="+", command=add_task).pack(side=tk.LEFT)


    def descargar_y_abrir_material(self, link):
        from Campus_cloud_elements.Material import descargar_y_abrir_desde_drive
        descargar_y_abrir_desde_drive(link)
    
    def create_section_with_add(self, frame, section_name, item_list, add_callback=None):
        items_frame = ttk.Frame(frame)
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def refresh_items():
            for widget in items_frame.winfo_children():
                widget.destroy()

            if section_name == "Material" and hasattr(item_list, "items"):
                for name, link in item_list.items():
                    item_frame = ttk.Frame(items_frame)
                    item_frame.pack(fill=tk.X, pady=2)
                    ttk.Label(item_frame, text=name).pack(side=tk.LEFT, padx=5)
                    open_button = ttk.Button(item_frame, text="Abrir", width=6, command=lambda l=link: self.descargar_y_abrir_material(l))
                    open_button.pack(side=tk.RIGHT)
                    delete_button = ttk.Button(item_frame, text="✖", width=3, command=lambda n=name: eliminar_material(n))
                    delete_button.pack(side=tk.RIGHT, padx=(0, 5))

            elif section_name == "Nota":
                for idx, item in enumerate(item_list):
                    item_frame = ttk.Frame(items_frame)
                    item_frame.pack(fill=tk.X, pady=2)

                    is_editing = tk.BooleanVar(value=False)

                    tarea_lbl = ttk.Label(item_frame, text=f"{item.get('Tarea', f'Tarea {idx+1}')}")
                    tarea_lbl.pack(side=tk.LEFT, padx=5)

                    nota_var = tk.StringVar(value=item.get("Nota", ""))
                    peso_var = tk.StringVar(value=item.get("Peso", ""))

                    nota_entry = ttk.Entry(item_frame, width=5, textvariable=nota_var, state="disabled")
                    peso_entry = ttk.Entry(item_frame, width=5, textvariable=peso_var, state="disabled")

                    def toggle_edit(entry1=nota_entry, entry2=peso_entry, var=is_editing):
                        if var.get():
                            entry1.configure(state="disabled")
                            entry2.configure(state="disabled")
                            var.set(False)
                        else:
                            entry1.configure(state="normal")
                            entry2.configure(state="normal")
                            var.set(True)

                    def guardar(idx=idx, e1=nota_entry, e2=peso_entry):
                        item_list[idx]["Nota"] = e1.get()
                        item_list[idx]["Peso"] = e2.get()
                        if self.current_subject:
                            self.current_subject.save_to_file()
                        toggle_edit()

                    ttk.Label(item_frame, text="Nota:").pack(side=tk.LEFT)
                    nota_entry.pack(side=tk.LEFT, padx=2)
                    ttk.Label(item_frame, text="Peso %:").pack(side=tk.LEFT)
                    peso_entry.pack(side=tk.LEFT, padx=2)

                    ttk.Button(item_frame, text="Editar", command=toggle_edit).pack(side=tk.LEFT, padx=2)
                    ttk.Button(item_frame, text="Guardar", command=guardar).pack(side=tk.LEFT, padx=2)

            else:
                for idx, item in enumerate(item_list):
                    item_frame = ttk.Frame(items_frame)
                    item_frame.pack(fill=tk.X, pady=2)
                    ttk.Label(item_frame, text=str(item)).pack(anchor=tk.W)

        def eliminar_material(nombre):
            item_list.remove(nombre)
            if self.current_subject:
                self.current_subject.save_to_file()
            refresh_items()

        refresh_items()

        add_frame = ttk.Frame(frame)
        add_frame.pack(fill=tk.X, padx=10, pady=10)

        if section_name == "Material":
            ttk.Label(add_frame, text="Nombre:").pack(side=tk.LEFT)
            name_entry = ttk.Entry(add_frame, width=20)
            name_entry.pack(side=tk.LEFT, padx=5)
            ttk.Label(add_frame, text="Link:").pack(side=tk.LEFT)
            link_entry = ttk.Entry(add_frame)
            link_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

            def add_item():
                name = name_entry.get().strip()
                link = link_entry.get().strip()
                if name and link:
                    item_list.add(name, link)
                    if self.current_subject:
                        self.current_subject.save_to_file()
                    refresh_items()
                    name_entry.delete(0, tk.END)
                    link_entry.delete(0, tk.END)

            ttk.Button(add_frame, text="+", command=add_item).pack(side=tk.LEFT)

        elif section_name == "Nota":
            ttk.Label(add_frame, text="Nombre:").pack(side=tk.LEFT)
            nombre_entry = ttk.Entry(add_frame, width=15)
            nombre_entry.pack(side=tk.LEFT, padx=5)
            ttk.Label(add_frame, text="Nota:").pack(side=tk.LEFT)
            nota_entry = ttk.Entry(add_frame, width=5)
            nota_entry.pack(side=tk.LEFT, padx=5)
            ttk.Label(add_frame, text="Peso %:").pack(side=tk.LEFT)
            peso_entry = ttk.Entry(add_frame, width=5)
            peso_entry.pack(side=tk.LEFT, padx=5)

            def add_manual_nota():
                nombre = nombre_entry.get().strip()
                nota = nota_entry.get().strip()
                peso = peso_entry.get().strip()
                if nombre and nota:
                    item_list.append({"Tarea": nombre, "Nota": nota, "Peso": peso})
                    if self.current_subject:
                        self.current_subject.save_to_file()
                    refresh_items()
                    nombre_entry.delete(0, tk.END)
                    nota_entry.delete(0, tk.END)
                    peso_entry.delete(0, tk.END)

            ttk.Button(add_frame, text="+", command=add_manual_nota).pack(side=tk.LEFT)
if __name__ == "__main__":
    

    def on_close():
        Subject.export_all_to_excel()
        try:
            upload_excel_to_drive()
        except Exception as e:
            print(f"Error subiendo a Drive: {e}")
        root.destroy()

    try:
        download_excel_from_drive()
    except Exception as e:
        print(f"Error descargando desde Drive: {e}")

    root = tk.Tk()
    app = CampusCloudApp(root)
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
