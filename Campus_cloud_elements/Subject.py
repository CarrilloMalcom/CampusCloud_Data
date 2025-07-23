from collections import deque
from datetime import datetime
import os
import json
import pandas as pd
from Campus_cloud_elements.Material import MaterialTable


class Subject:
    def __init__(self, name, credits):
        self.__name__ = name 
        self.__tasks__ = []
        self.__completed_tasks__ = []
        self.__grades__ = []
        self.__material__ = MaterialTable()
        self.__credits__ = credits
        self.__ToDoQueue__ = deque()

    @property
    def name(self):
        return self.__name__

    @property
    def credits(self):
        return self.__credits__

    @property
    def grades(self):
        return self.__grades__

    @property
    def tasks(self):
        return self.__tasks__

    @property
    def completed_tasks(self):
        return self.__completed_tasks__

    @property
    def materials(self):
        return self.__material__

    def addTask(self, task, DueDate):
        if not isinstance(DueDate, datetime):
            try: 
                DueDate = datetime.strptime(DueDate, "%Y-%m-%d")
            except ValueError:
                print("Formato de fecha incorrecto. Debe ser: YYYY-MM-DD.")
                return None

        Task_info = {"Estado": task, "Completada": False, "DueDate": DueDate}
        self.__tasks__.append(Task_info)
        self.__tasks__.sort(key=lambda x: x["DueDate"])

        converter = list(self.__ToDoQueue__)
        converter.append(Task_info)
        converter.sort(key=lambda x: x["DueDate"])
        self.__ToDoQueue__ = deque(converter)

        self.save_to_file()

    def Completetasks(self, Index):   
        if 0 <= Index < len(self.__tasks__):
            task = self.__tasks__.pop(Index)  
            task["Completada"] = True
            self.__completed_tasks__.append(task)
            print(f"Tarea '{task['Estado']}' marcada como completada y movida a tareas completadas.")
            try:
                self.__ToDoQueue__.remove(task)
            except ValueError:
                pass
        else:
            print("No Existe la tarea")

        self.save_to_file()

    def DeleteTask(self, Index):
        if 0 <= Index < len(self.__tasks__):
            deleted_task = self.__tasks__.pop(Index)
            print(f"Tarea eliminada: {deleted_task['Estado']}")
            try:
                self.__ToDoQueue__.remove(deleted_task)
            except ValueError:
                pass
        else:
            print("No existe la tarea")

        self.save_to_file()

    def addMaterial(self, name, link):
        if name and link:
            self.__material__.add(name, link)
            self.save_to_file()

    @property 
    def Subjectcredits(self):
        return self.__credits__ 

    def addMaterialFromImport(self, name, link):
        self.__material__.add(name, link)

    def save_to_file(self):
        data = {
            "name": self.__name__,
            "credits": self.__credits__,
            "tasks": [
                {
                    "Estado": t["Estado"],
                    "Completada": t["Completada"],
                    "DueDate": t["DueDate"].strftime("%Y-%m-%d")
                } for t in self.__tasks__
            ],
            "completed_tasks": [
                {
                    "Estado": t["Estado"],
                    "Completada": t["Completada"],
                    "DueDate": t["DueDate"].strftime("%Y-%m-%d")
                } for t in self.__completed_tasks__
            ],
            "grades": self.__grades__,
            "materials": self.__material__.to_dict()
        }
        folder = "subjects_data"
        os.makedirs(folder, exist_ok=True)
        filename = os.path.join(folder, f"{self.__name__}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_from_file(filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        subject = Subject(data["name"], data["credits"])
        for task in data["tasks"]:
            subject.__tasks__.append({
                "Estado": task["Estado"],
                "Completada": task["Completada"],
                "DueDate": datetime.strptime(task["DueDate"], "%Y-%m-%d")
            })
        for task in data["completed_tasks"]:
            subject.__completed_tasks__.append({
                "Estado": task["Estado"],
                "Completada": task["Completada"],
                "DueDate": datetime.strptime(task["DueDate"], "%Y-%m-%d")
            })
        subject.__grades__ = data["grades"]
        subject.__material__ = MaterialTable()
        subject.__material__.load_from_dict(data.get("materials", {}))
        subject.__ToDoQueue__ = deque(sorted(subject.__tasks__, key=lambda x: x["DueDate"]))
        return subject

    @staticmethod
    def export_all_to_excel(folder="subjects_data", output_file="subjects_data.xlsx"):
        subjects = []
        tasks = []
        completed = []
        grades = []
        materials = []

        if not os.path.exists(folder):
            return

        for file in os.listdir(folder):
            if not file.endswith(".txt"):
                continue
            path = os.path.join(folder, file)
            subj = Subject.load_from_file(path)
            subjects.append({"name": subj.name, "credits": subj.credits})
            for t in subj.tasks:
                tasks.append({"subject": subj.name, "estado": t["Estado"], "completada": t["Completada"], "fecha": t["DueDate"].strftime("%Y-%m-%d")})
            for t in subj.completed_tasks:
                completed.append({"subject": subj.name, "estado": t["Estado"], "completada": t["Completada"], "fecha": t["DueDate"].strftime("%Y-%m-%d")})
            for g in subj.grades:
                grades.append({"subject": subj.name, "grade": g})
            for name, link in subj.materials.items():
                materials.append({"subject": subj.name, "material_name": name, "material_link": link})

        excel_path = os.path.join(folder, output_file)

        with pd.ExcelWriter(excel_path) as writer:
            pd.DataFrame(subjects).to_excel(writer, sheet_name="Subjects", index=False)
            pd.DataFrame(tasks).to_excel(writer, sheet_name="Tasks", index=False)
            pd.DataFrame(completed).to_excel(writer, sheet_name="CompletedTasks", index=False)
            pd.DataFrame(grades).to_excel(writer, sheet_name="Grades", index=False)
            pd.DataFrame(materials).to_excel(writer, sheet_name="Materials", index=False)

        for file in os.listdir(folder):
            if file.endswith(".txt"):
                os.remove(os.path.join(folder, file))

    @staticmethod
    def import_all_from_excel(excel_file="subjects_data/subjects_data.xlsx", output_folder="subjects_data"):
        if not os.path.exists(excel_file):
            return

        os.makedirs(output_folder, exist_ok=True)
        df_subjects = pd.read_excel(excel_file, sheet_name=None)

        subjects_dict = {}

        for row in df_subjects["Subjects"].to_dict("records"):
            subject = Subject(row["name"], row["credits"])
            subjects_dict[row["name"]] = subject

        for row in df_subjects["Tasks"].to_dict("records"):
            subject = subjects_dict.get(row["subject"])
            if subject:
                subject.addTask(row["estado"], row["fecha"])

        for row in df_subjects["CompletedTasks"].to_dict("records"):
            subject = subjects_dict.get(row["subject"])
            if subject:
                task = {"Estado": row["estado"], "Completada": True, "DueDate": datetime.strptime(row["fecha"], "%Y-%m-%d")}
                subject._Subject__completed_tasks__.append(task)

        for row in df_subjects["Grades"].to_dict("records"):
            subject = subjects_dict.get(row["subject"])
            if subject:
                subject._Subject__grades__.append(row["grade"])

        for row in df_subjects["Materials"].to_dict("records"):
            subject = subjects_dict.get(row["subject"])
            if subject:
                subject.addMaterialFromImport(row["material_name"], row["material_link"])

        for subject in subjects_dict.values():
            subject.save_to_file()
