# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import json
import os

class PatientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Пациенты")
        
        # Кросс-платформенный путь к файлу
        self.data_file = os.path.join(os.path.dirname(__file__), "patients.json")
        self.patients = self.load_data()
        
        self.create_widgets()
        self.update_table()

    def create_widgets(self):
        # Таблица пациентов
        columns = ("ФИО", "Возраст", "Пол", "Рост", "Вес", "ИМТ")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        
        # Устанавливаем ширину колонок
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Фрейм с кнопками
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Добавить", command=self.add_patient).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Редактировать", command=self.edit_patient).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Статистика", command=self.show_stats).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Удалить", command=self.delete_patient).pack(side=tk.LEFT, padx=2)

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
            return []

    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.patients, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def calculate_bmi(self, weight, height):
        return round(weight / ((height / 100) ** 2), 2)

    def update_table(self):
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Сортируем пациентов по ФИО перед выводом
        sorted_patients = sorted(self.patients, key=lambda x: x['name'])
        
        # Заполняем таблицу отсортированными данными
        for patient in sorted_patients:
            self.tree.insert("", tk.END, values=(
                patient['name'],
                patient['age'],
                patient['gender'],
                patient['height'],
                patient['weight'],
                patient['bmi']
            ))

    def add_patient(self):
        self.edit_patient_window(is_new=True)

    def edit_patient(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите пациента для редактирования")
            return
        self.edit_patient_window(is_new=False, item=selected[0])

    def delete_patient(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите пациента для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранного пациента?"):
            idx = self.tree.index(selected[0])
            self.patients.pop(idx)
            self.save_data()
            self.update_table()

    def edit_patient_window(self, is_new, item=None):
        window = tk.Toplevel(self.root)
        window.title("Добавить пациента" if is_new else "Редактировать пациента")
        
        entries = {}
        default_values = ["", "", "", "", ""]
        
        if not is_new:
            patient_data = self.tree.item(item)['values']
            default_values = [
                patient_data[0],
                patient_data[1],
                patient_data[2],
                patient_data[3],
                patient_data[4]
            ]

        # Поля ввода
        labels = ["ФИО:", "Возраст:", "Пол (м/ж):", "Рост (см):", "Вес (кг):"]
        for i, label in enumerate(labels):
            tk.Label(window, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = tk.Entry(window)
            entry.insert(0, default_values[i])
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[label] = entry

        def save():
            try:
                new_patient = {
                    'name': entries["ФИО:"].get(),
                    'age': int(entries["Возраст:"].get()),
                    'gender': entries["Пол (м/ж):"].get().lower(),
                    'height': float(entries["Рост (см):"].get()),
                    'weight': float(entries["Вес (кг):"].get())
                }
                new_patient['bmi'] = self.calculate_bmi(new_patient['weight'], new_patient['height'])
                
                if is_new:
                    self.patients.append(new_patient)
                else:
                    idx = self.tree.index(item)
                    self.patients[idx] = new_patient
                
                self.save_data()
                self.update_table()
                window.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Проверьте правильность введенных данных")

        tk.Button(window, text="Сохранить", command=save).grid(row=5, columnspan=2, pady=10)

    def show_stats(self):
        if not self.patients:
            messagebox.showwarning("Ошибка", "Нет данных для статистики")
            return

        # Подготовка данных
        genders = [p['gender'] for p in self.patients]
        ages = [p['age'] for p in self.patients]
        bmis = [p['bmi'] for p in self.patients]

        # Создание графиков
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

        # Распределение по полу
        gender_counts = {'м': genders.count('м'), 'ж': genders.count('ж')}
        ax1.pie(gender_counts.values(), labels=gender_counts.keys(), autopct='%1.1f%%')
        ax1.set_title('Распределение по полу')

        # Распределение по возрасту
        ax2.hist(ages, bins=8, edgecolor='black')
        ax2.set_title('Распределение по возрасту')
        ax2.set_xlabel('Возраст')
        ax2.set_ylabel('Количество')

        # Распределение ИМТ по полу
        m_bmi = [p['bmi'] for p in self.patients if p['gender'] == 'м']
        f_bmi = [p['bmi'] for p in self.patients if p['gender'] == 'ж']
        ax3.boxplot([m_bmi, f_bmi], labels=['М', 'Ж'])
        ax3.set_title('Распределение ИМТ по полу')
        ax3.set_ylabel('ИМТ')

        # Зависимость ИМТ от возраста
        colors = ['blue' if g == 'м' else 'red' for g in genders]
        ax4.scatter(ages, bmis, c=colors, alpha=0.6)
        ax4.set_title('Зависимость ИМТ от возраста')
        ax4.set_xlabel('Возраст')
        ax4.set_ylabel('ИМТ')
        ax4.legend(['Мужчины', 'Женщины'])

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # Проверяем доступность matplotlib
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Ошибка: Установите matplotlib: pip install matplotlib")
        exit(1)
    
    root = tk.Tk()
    root.geometry("800x400")  # Фиксированный размер окна
    app = PatientApp(root)
    root.mainloop()
