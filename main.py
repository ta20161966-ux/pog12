import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import json
from datetime import datetime

class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.root.geometry("700x500")
        self.records = []
        self.filename = "data.json"
        
        self.create_menu()
        self.create_widgets()
        self.load_data()
        self.update_treeview()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Сохранить", command=self.save_data)
        filemenu.add_command(label="Загрузить", command=self.load_data_dialog)
        menubar.add_cascade(label="Файл", menu=filemenu)
        self.root.config(menu=menubar)

    def create_widgets(self):
        # --- Frame for Input ---
        frame_input = ttk.LabelFrame(self.root, text="Новая запись", padding="10")
        frame_input.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_input, text="Дата:").grid(row=0, column=0, sticky="w")
        self.date_entry = DateEntry(frame_input, width=12, background='darkblue',
                                    foreground='white', borderwidth=2)
        self.date_entry.grid(row=0, column=1, sticky="w", pady=5)

        ttk.Label(frame_input, text="Температура (°C):").grid(row=1, column=0, sticky="w")
        self.temp_entry = ttk.Entry(frame_input, width=15)
        self.temp_entry.grid(row=1, column=1, sticky="w", pady=5)

        ttk.Label(frame_input, text="Описание:").grid(row=2, column=0, sticky="nw")
        self.desc_entry = ttk.Entry(frame_input, width=25)
        self.desc_entry.grid(row=2, column=1, sticky="w", pady=5)

        self.rain_var = tk.BooleanVar()
        ttk.Checkbutton(frame_input, text="Осадки", variable=self.rain_var).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=5)

        ttk.Button(frame_input, text="Добавить запись", command=self.add_record).grid(
            row=4, column=0, columnspan=2, pady=10)

        # --- Frame for Filters ---
        frame_filters = ttk.LabelFrame(self.root, text="Фильтры", padding="10")
        frame_filters.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_filters, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w")
        self.filter_date = ttk.Entry(frame_filters, width=15)
        self.filter_date.grid(row=0, column=1, sticky="w", pady=5)
        
        ttk.Label(frame_filters, text="Температура выше (°C):").grid(row=1, column=0, sticky="w")
        self.filter_temp = ttk.Entry(frame_filters, width=15)
        self.filter_temp.grid(row=1, column=1, sticky="w", pady=5)
        
        ttk.Button(frame_filters, text="Применить фильтр", command=self.apply_filter).grid(
            row=2, column=0, columnspan=2, pady=5)
        
        ttk.Button(frame_filters, text="Сбросить фильтр", command=self.reset_filter).grid(
            row=3, column=0, columnspan=2, pady=5)

        # --- Treeview for Records ---
        columns = ("date", "temp", "desc", "rain")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура (°C)")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("rain", text="Осадки")
        
        self.tree.column("date", width=120)
        self.tree.column("temp", width=100)
        self.tree.column("desc", width=300)
        self.tree.column("rain", width=80)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

    def add_record(self):
        date_str = self.date_entry.get_date().strftime("%Y-%m-%d")
        
        try:
            temp = float(self.temp_entry.get())
            if temp < -100 or temp > 100:
                raise ValueError("Температура вне диапазона.")
            temp_str = f"{temp:.1f}"
            self.temp_entry.config(style="TEntry")
            self.temp_entry.update()
            
            if not self.desc_entry.get().strip():
                raise ValueError("Описание не может быть пустым.")
                
            record = {
                "date": date_str,
                "temp": temp_str,
                "desc": self.desc_entry.get().strip(),
                "rain": "Да" if self.rain_var.get() else "Нет"
            }
            
            self.records.append(record)
            self.update_treeview()
            
            # Очистка полей после добавления
            self.desc_entry.delete(0, tk.END)
            self.temp_entry.delete(0, tk.END)
            self.rain_var.set(False)
            
            messagebox.showinfo("Успех", "Запись добавлена!")
            
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            self.temp_entry.config(style="Error.TEntry")
            self.temp_entry.update()

    def update_treeview(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        for record in self.records:
            self.tree.insert("", "end", values=(record["date"], record["temp"], record["desc"], record["rain"]))
    
    def apply_filter(self):
        filter_date = self.filter_date.get().strip()
        filter_temp_str = self.filter_temp.get().strip()
        
        filtered_records = self.records.copy()
        
        if filter_date:
            try:
                datetime.strptime(filter_date, "%Y-%m-%d")
                filtered_records = [r for r in filtered_records if r["date"] == filter_date]
            except ValueError:
                messagebox.showerror("Ошибка фильтра", "Дата должна быть в формате ГГГГ-ММ-ДД")
                return

        
        if filter_temp_str:
            try:
                filter_temp = float(filter_temp_str)
                filtered_records = [r for r in filtered_records if float(r["temp"]) > filter_temp]
            except ValueError:
                messagebox.showerror("Ошибка фильтра", "Температура должна быть числом")
                return

        
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        for record in filtered_records:
            self.tree.insert("", "end", values=(record["date"], record["temp"], record["desc"], record["rain"]))
    
    def reset_filter(self):
         # Просто обновляем дерево всеми записями
         self.update_treeview()
         # Очищаем поля фильтра
         self.filter_date.delete(0, tk.END)
         self.filter_temp.delete(0, tk.END)
    
    def save_data(self):
         try:
             with open(self.filename, 'w', encoding='utf-8') as f:
                 json.dump(self.records, f, ensure_ascii=False, indent=4)
             messagebox.showinfo("Успех", f"Данные сохранены в {self.filename}")
         except Exception as e:
             messagebox.showerror("Ошибка сохранения", str(e))
    
    def load_data_dialog(self):
         filename = filedialog.askopenfilename(
             filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
         )
         if filename:
             try:
                 with open(filename, 'r', encoding='utf-8') as f:
                     data = json.load(f)
                 if isinstance(data, list) and all(isinstance(x, dict) for x in data):
                     self.records = data
                     self.filename = filename  # Обновляем текущий файл
                     self.update_treeview()
                     messagebox.showinfo("Успех", f"Данные загружены из {filename}")
                 else:
                     raise ValueError("Неверный формат данных в файле.")
             except Exception as e:
                 messagebox.showerror("Ошибка загрузки", str(e))
    
    def load_data(self):
         try:
             with open(self.filename, 'r', encoding='utf-8') as f:
                 data = json.load(f)
             if isinstance(data, list) and all(isinstance(x, dict) for x in data):
                 self.records = data
             else:
                 raise ValueError("Неверный формат данных в файле.")
         except (FileNotFoundError, json.JSONDecodeError):
             # Если файла нет или он пустой/битый — начинаем с пустого списка.
             self.records = []


if __name__ == "__main__":
    root = tk.Tk()
    
    # Настройка стилей для визуальной обратной связи об ошибках.
    style = ttk.Style()
    style.configure("Error.TEntry", fieldbackground="#f7d7da")  # Светло-красный фон

    app = WeatherDiaryApp(root)
    root.mainloop()
