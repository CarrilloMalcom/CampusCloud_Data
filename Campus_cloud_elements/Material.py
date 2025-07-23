class MaterialTable:
    def __init__(self, capacity=50):
        self.capacity = capacity
        self.table = [[] for _ in range(capacity)] 

    def _hash(self, key):
        return hash(key) % self.capacity

    def add(self, name, link):
        index = self._hash(name)
        for i, (k, _) in enumerate(self.table[index]):
            if k == name:
                self.table[index][i] = (name, link)  
                return
        self.table[index].append((name, link)) 

    def get(self, name):
        index = self._hash(name)
        for k, v in self.table[index]:
            if k == name:
                return v
        return None

    def remove(self, name):
        index = self._hash(name)
        self.table[index] = [(k, v) for k, v in self.table[index] if k != name]

    def items(self):
        for bucket in self.table:
            for k, v in bucket:
                yield k, v

    def to_dict(self):
        return {k: v for k, v in self.items()}

    def load_from_dict(self, d):
        for k, v in d.items():
            self.add(k, v)

def descargar_y_abrir_desde_drive(link):
    import gdown
    import os
    import platform
    import subprocess
    import threading
    import time

    folder = "subjects_data"
    os.makedirs(folder, exist_ok=True)
    output = os.path.join(folder, "temporal_documento.pdf")

    try:
        result = gdown.download(link, output, quiet=False, fuzzy=True)
        if result is None or not os.path.exists(output):
            print("No se pudo descargar el archivo. Verifica los permisos en Google Drive.")
            return

        sistema = platform.system()
        if sistema == 'Windows':
            subprocess.Popen(['start', '', output], shell=True)
        elif sistema == 'Darwin':
            subprocess.Popen(['open', output])
        else:
            subprocess.Popen(['xdg-open', output])

        def intentar_eliminar():
            time.sleep(10) 
            while True:
                try:
                    if os.path.exists(output):
                        os.remove(output)
                        print("Archivo eliminado exitosamente.")
                        break
                except Exception:
                    pass
                time.sleep(5)
        threading.Thread(target=intentar_eliminar, daemon=True).start()

    except Exception as e:
        print(f"Error al manejar el archivo: {e}")
