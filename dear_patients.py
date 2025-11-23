import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')
import json
import os
from PIL import Image, ImageTk, ImageDraw
import seaborn as sns
import numpy as np
import math

# Бежево-фисташковая цветовая палитра
PRIMARY_BG = "#f5f5dc"
SECONDARY_BG = "#e8f8f5"
ACCENT_BLUE = "#93c572"
ACCENT_GREEN = "#78b478"
ACCENT_ORANGE = "#c8a87c"
ACCENT_RED = "#d2a679"
TEXT_PRIMARY = "#556b2f"
TEXT_SECONDARY = "#8a9a5b"
CHART_BG = "#e8f8f5"
CHART_TEXT = "#556b2f"
HOVER_BLUE = "#7da860"
HOVER_GREEN = "#659965"
HOVER_ORANGE = "#b0956b"
HOVER_RED = "#c1956c"

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=200, height=40, 
                 corner_radius=20, bg_color=ACCENT_BLUE, text_color='white', 
                 hover_color=HOVER_BLUE, font=('Georgia', 10, 'bold italic')):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bg=PRIMARY_BG)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.corner_radius = corner_radius
        self.font = font
        self.text = text
        self.is_pressed = False
        
        self.draw_button(bg_color)
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
    def draw_button(self, color):
        self.delete("all")
        self.create_rounded_rect(5, 5, self.winfo_reqwidth()-5, 
                               self.winfo_reqheight()-5, 
                               self.corner_radius, fill=color, outline="")
        self.create_text(self.winfo_reqwidth()//2, self.winfo_reqheight()//2, 
                        text=self.text, fill=self.text_color, font=self.font)
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1,
                 x2-radius, y1,
                 x2, y1,
                 x2, y1+radius,
                 x2, y2-radius,
                 x2, y2,
                 x2-radius, y2,
                 x1+radius, y2,
                 x1, y2,
                 x1, y2-radius,
                 x1, y1+radius,
                 x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_click(self, event):
        self.is_pressed = True
        self.draw_button(self.hover_color)
        self.after(150, self.reset_button)
        self.command()
    
    def reset_button(self):
        self.is_pressed = False
        self.draw_button(self.bg_color)
    
    def on_enter(self, event):
        if not self.is_pressed:
            self.draw_button(self.hover_color)
    
    def on_leave(self, event):
        if not self.is_pressed:
            self.draw_button(self.bg_color)

class ImageLoader:
    def __init__(self):
        self.images = {}
        
    def load_images(self):
        try:
            self.images['header_icon'] = self.load_image('header_icon.png', (64, 64))
            self.images['clinic_logo'] = self.load_image('clinic_logo.png', (200, 100))
            self.images['tools_decor'] = self.load_image('tools_decor.png', (40, 40))
            self.images['patient_avatar'] = self.load_image('patient_avatar.png', (100, 100))
            self.images['stats_decor'] = self.load_image('stats_decor.png', (50, 50))
            print("Все изображения успешно загружены!")
        except Exception as e:
            print(f"Ошибка загрузки изображений: {e}")
    
    def load_image(self, filename, size=None):
        image_path = os.path.join('images', filename)
        if not os.path.exists(image_path):
            print(f"Файл {image_path} не найден")
            return None
        image = Image.open(image_path)
        if size:
            image = image.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)
    
    def get_image(self, name):
        return self.images.get(name)

class MedicalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Медицинская система учета пациентов")
        self.root.geometry("1400x900")
        self.root.configure(bg=PRIMARY_BG)
        
        self.image_loader = ImageLoader()
        self.image_loader.load_images()
        
        self.patients_file = "patients.json"
        self.patients = self.load_patients()
        
        self.setup_styles()
        self.create_interface()
        
        self.chart_canvases = []
        self.selected_patient_index = None
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Modern.TFrame', background=PRIMARY_BG)
        style.configure('Title.TLabel', 
                       background=PRIMARY_BG, 
                       foreground=TEXT_PRIMARY,
                       font=('Georgia', 16, 'bold italic'))
        
        style.configure('Subtitle.TLabel',
                       background=PRIMARY_BG,
                       foreground=TEXT_PRIMARY,
                       font=('Georgia', 12, 'bold italic'))
        
        style.configure('Regular.TLabel',
                       background=PRIMARY_BG,
                       foreground=TEXT_PRIMARY,
                       font=('Georgia', 10, 'normal'))
        
        style.configure('Modern.TButton',
                       background=ACCENT_BLUE,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Georgia', 10, 'bold italic'))
        style.map('Modern.TButton',
                 background=[('active', HOVER_BLUE)])
        
        style.configure('Modern.TEntry',
                       fieldbackground='white',
                       borderwidth=2,
                       relief='flat',
                       font=('Georgia', 10))
    
    def create_interface(self):
        main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.create_header(main_frame)
        self.create_logo_section(main_frame)
        self.create_control_panel(main_frame)
        self.create_patients_table(main_frame)
        
        self.charts_container = ttk.Frame(main_frame, style='Modern.TFrame')
        
    def create_header(self, parent):
        header_frame = ttk.Frame(parent, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        header_icon = self.image_loader.get_image('header_icon')
        if header_icon:
            icon_label = tk.Label(header_frame, image=header_icon, bg=PRIMARY_BG)
            icon_label.pack(side='left', padx=10)
        
        title_label = ttk.Label(header_frame, 
                               text="Медицинская система учета пациентов", 
                               style='Title.TLabel')
        title_label.pack(side='left')
        
    def create_logo_section(self, parent):
        logo_frame = ttk.Frame(parent, style='Modern.TFrame')
        logo_frame.pack(fill='x', pady=10)
        
        clinic_logo = self.image_loader.get_image('clinic_logo')
        if clinic_logo:
            logo_label = tk.Label(logo_frame, image=clinic_logo, bg=PRIMARY_BG)
            logo_label.pack(pady=20)
        else:
            logo_placeholder = ttk.Label(logo_frame, 
                                       text="Логотип клиники", 
                                       background=SECONDARY_BG,
                                       foreground=TEXT_PRIMARY,
                                       font=('Georgia', 12, 'italic'))
            logo_placeholder.pack(pady=20)
        
    def create_control_panel(self, parent):
        control_frame = ttk.Frame(parent, style='Modern.TFrame')
        control_frame.pack(fill='x', pady=10)
        
        tools_icon = self.image_loader.get_image('tools_decor')
        if tools_icon:
            tools_label = tk.Label(control_frame, image=tools_icon, bg=PRIMARY_BG)
            tools_label.pack(side='left', padx=10)
        
        buttons_frame = ttk.Frame(control_frame, style='Modern.TFrame')
        buttons_frame.pack(side='left', padx=20)
        
        RoundedButton(buttons_frame, "Добавить пациента", 
                     command=self.add_patient, 
                     width=180, height=35, bg_color=ACCENT_BLUE,
                     hover_color=HOVER_BLUE).pack(side='left', padx=5)
        
        RoundedButton(buttons_frame, "Редактировать", 
                     command=self.edit_patient,
                     width=150, height=35, bg_color=ACCENT_GREEN,
                     hover_color=HOVER_GREEN).pack(side='left', padx=5)
        
        RoundedButton(buttons_frame, "Статистика", 
                     command=self.show_statistics,
                     width=130, height=35, bg_color=ACCENT_ORANGE,
                     hover_color=HOVER_ORANGE).pack(side='left', padx=5)
        
        RoundedButton(buttons_frame, "Удалить", 
                     command=self.delete_patient,
                     width=100, height=35, bg_color=ACCENT_RED,
                     hover_color=HOVER_RED).pack(side='left', padx=5)
        
    def create_patients_table(self, parent):
        table_frame = ttk.Frame(parent, style='Modern.TFrame')
        table_frame.pack(fill='both', expand=True, pady=10)
        
        ttk.Label(table_frame, 
                 text="Список пациентов", 
                 style='Subtitle.TLabel').pack(anchor='w')
        
        columns = ("ФИО", "Возраст", "Пол", "Рост", "Вес", "ИМТ")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        
        style = ttk.Style()
        style.configure("Treeview", font=('Georgia', 9), background="white", rowheight=25)
        style.configure("Treeview.Heading", font=('Georgia', 10, 'bold italic'), 
                       background=ACCENT_BLUE, foreground='white')
        style.map("Treeview.Heading", background=[('active', HOVER_BLUE)])
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_patient_select)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.load_patients_data()
    
    def on_patient_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = selected[0]
            index = self.tree.index(item)
            self.selected_patient_index = index
        else:
            self.selected_patient_index = None
        
    def load_patients_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for patient in self.patients:
            bmi = self.calculate_bmi(patient['weight'], patient['height'])
            self.tree.insert("", "end", values=(
                patient['name'],
                patient['age'],
                patient['gender'],
                patient['height'],
                patient['weight'],
                f"{bmi:.1f}"
            ))
    
    def calculate_bmi(self, weight, height):
        try:
            height = float(height)
            weight = float(weight)
            
            if height <= 0 or weight <= 0:
                return float('nan')
                
            height_m = height / 100
            bmi = weight / (height_m ** 2)
            
            if bmi < 10 or bmi > 100:
                return float('nan')
                
            return bmi
        except (ValueError, TypeError, ZeroDivisionError):
            return float('nan')
    
    def save_patients(self):
        try:
            with open(self.patients_file, 'w', encoding='utf-8') as f:
                json.dump(self.patients, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
            return False
    
    def add_patient(self):
        self.show_patient_form()
    
    def edit_patient(self):
        if self.selected_patient_index is None:
            messagebox.showwarning("Внимание", "Выберите пациента для редактирования")
            return
        
        patient_data = self.patients[self.selected_patient_index]
        self.show_patient_form(patient_data, self.selected_patient_index)
    
    def show_patient_form(self, patient_data=None, patient_index=None):
        form_window = tk.Toplevel(self.root)
        form_window.title("Редактирование пациента" if patient_data else "Новый пациент")
        form_window.geometry("400x500")
        form_window.configure(bg=PRIMARY_BG)
        form_window.resizable(False, False)
        
        form_window.transient(self.root)
        form_window.grab_set()
        
        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.gender_var = tk.StringVar(value="М")
        self.height_var = tk.StringVar()
        self.weight_var = tk.StringVar()
        
        if patient_data:
            self.name_var.set(patient_data.get('name', ''))
            self.age_var.set(str(patient_data.get('age', '')))
            self.gender_var.set(patient_data.get('gender', 'М'))
            self.height_var.set(str(patient_data.get('height', '')))
            self.weight_var.set(str(patient_data.get('weight', '')))
        
        avatar = self.image_loader.get_image('patient_avatar')
        if avatar:
            avatar_label = tk.Label(form_window, image=avatar, bg=PRIMARY_BG)
            avatar_label.pack(pady=10)
        
        form_frame = ttk.Frame(form_window, style='Modern.TFrame')
        form_frame.pack(fill='both', expand=True, padx=20)
        
        ttk.Label(form_frame, text="ФИО пациента:", style='Subtitle.TLabel').pack(anchor='w', pady=(10, 5))
        name_entry = ttk.Entry(form_frame, width=30, textvariable=self.name_var, font=('Georgia', 10))
        name_entry.pack(fill='x', pady=5)
        
        ttk.Label(form_frame, text="Возраст:", style='Subtitle.TLabel').pack(anchor='w', pady=(10, 5))
        age_entry = ttk.Entry(form_frame, width=30, textvariable=self.age_var, font=('Georgia', 10))
        age_entry.pack(fill='x', pady=5)
        
        ttk.Label(form_frame, text="Пол:", style='Subtitle.TLabel').pack(anchor='w', pady=(10, 5))
        gender_frame = ttk.Frame(form_frame, style='Modern.TFrame')
        gender_frame.pack(fill='x', pady=5)
        ttk.Radiobutton(gender_frame, text="Мужской", variable=self.gender_var, value="М").pack(side='left', padx=10)
        ttk.Radiobutton(gender_frame, text="Женский", variable=self.gender_var, value="Ж").pack(side='left', padx=10)
        
        ttk.Label(form_frame, text="Рост (см):", style='Subtitle.TLabel').pack(anchor='w', pady=(10, 5))
        height_entry = ttk.Entry(form_frame, width=30, textvariable=self.height_var, font=('Georgia', 10))
        height_entry.pack(fill='x', pady=5)
        
        ttk.Label(form_frame, text="Вес (кг):", style='Subtitle.TLabel').pack(anchor='w', pady=(10, 5))
        weight_entry = ttk.Entry(form_frame, width=30, textvariable=self.weight_var, font=('Georgia', 10))
        weight_entry.pack(fill='x', pady=5)
        
        button_frame = ttk.Frame(form_frame, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=20)
        
        save_text = "Сохранить изменения" if patient_data else "Добавить пациента"
        save_command = lambda: self.save_patient_data(patient_index, form_window)
        
        RoundedButton(button_frame, save_text, 
                     command=save_command,
                     width=200, height=40, bg_color=ACCENT_GREEN,
                     hover_color=HOVER_GREEN).pack()
    
    def save_patient_data(self, patient_index, window):
        if not self.name_var.get().strip():
            messagebox.showwarning("Ошибка", "Введите ФИО пациента")
            return
        
        try:
            age = int(self.age_var.get())
            height = float(self.height_var.get())
            weight = float(self.weight_var.get())
            
            if age <= 0 or height <= 0 or weight <= 0:
                raise ValueError("Значения должны быть положительными")
                
        except ValueError as e:
            messagebox.showwarning("Ошибка", "Проверьте корректность введенных данных:\n- Возраст - целое число\n- Рост и вес - числа больше 0")
            return
        
        patient_data = {
            'name': self.name_var.get().strip(),
            'age': age,
            'gender': self.gender_var.get(),
            'height': height,
            'weight': weight
        }
        
        if patient_index is not None:
            self.patients[patient_index] = patient_data
        else:
            self.patients.append(patient_data)
        
        if self.save_patients():
            self.load_patients_data()
            window.destroy()
            messagebox.showinfo("Успех", "Данные пациента сохранены")
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить данные")
    
    def delete_patient(self):
        if self.selected_patient_index is None:
            messagebox.showwarning("Внимание", "Выберите пациента для удаления")
            return
        
        patient_name = self.patients[self.selected_patient_index]['name']
        
        result = messagebox.askyesno(
            "Подтверждение удаления", 
            f"Вы уверены, что хотите удалить пациента:\n{patient_name}?",
            icon='warning'
        )
        
        if result:
            del self.patients[self.selected_patient_index]
            
            if self.save_patients():
                self.selected_patient_index = None
                self.load_patients_data()
                messagebox.showinfo("Успех", "Пациент удален")
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить пациента")
    
    def show_statistics(self):
        if not self.patients:
            messagebox.showinfo("Статистика", "Нет данных для построения графиков")
            return
            
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Медицинская статистика")
        stats_window.geometry("1200x800")
        stats_window.configure(bg=PRIMARY_BG)
        
        title_frame = ttk.Frame(stats_window, style='Modern.TFrame')
        title_frame.pack(fill='x', pady=10)
        
        stats_icon = self.image_loader.get_image('stats_decor')
        if stats_icon:
            icon_label = tk.Label(title_frame, image=stats_icon, bg=PRIMARY_BG)
            icon_label.pack(side='left', padx=10)
        
        ttk.Label(title_frame, 
                 text="Медицинская статистика", 
                 style='Title.TLabel').pack(side='left')
        
        canvas = tk.Canvas(stats_window, bg=PRIMARY_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(stats_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Modern.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")
        
        self.create_charts(scrollable_frame)
        
        button_frame = ttk.Frame(stats_window, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=10)
        
        RoundedButton(button_frame, "Закрыть статистику", 
                     command=stats_window.destroy,
                     width=200, height=40, bg_color=ACCENT_RED,
                     hover_color=HOVER_RED).pack()
    
    def create_charts(self, parent):
        try:
            self.create_gender_chart(parent)
            self.create_age_chart(parent)
            self.create_bmi_gender_chart(parent)
            self.create_bmi_age_chart(parent)
        except Exception as e:
            print(f"Ошибка создания графиков: {e}")
            error_frame = ttk.Frame(parent, style='Modern.TFrame')
            error_frame.pack(fill='x', pady=20)
            ttk.Label(error_frame, 
                     text=f"Ошибка при создании графиков: {str(e)}", 
                     style='Subtitle.TLabel',
                     foreground='red').pack()
    
    def create_gender_chart(self, parent):
        """График распределения по полу - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        gender_count = {'Мужчины': 0, 'Женщины': 0}
        
        # Отладочная информация
        print("=== ДАННЫЕ ПАЦИЕНТОВ ДЛЯ ГРАФИКА ПОЛА ===")
        for i, patient in enumerate(self.patients):
            gender = patient.get('gender', '')
            print(f"Пациент {i}: {patient.get('name')} - Пол: '{gender}'")
            
            # Универсальная проверка пола
            gender_str = str(gender).lower().strip()
            
            if any(word in gender_str for word in ['м', 'муж', 'male', 'мужской', 'мужчина']):
                gender_count['Мужчины'] += 1
                print(f"  -> Определен как Мужчина")
            elif any(word in gender_str for word in ['ж', 'жен', 'female', 'женский', 'женщина']):
                gender_count['Женщины'] += 1
                print(f"  -> Определен как Женщина")
            else:
                print(f"  -> Пол не распознан: '{gender}'")
        
        print(f"Итоговый подсчет: {gender_count}")
        print("=========================================")
        
        # Проверяем, есть ли данные для графика
        total_patients = sum(gender_count.values())
        if total_patients == 0:
            self.show_no_data_message(parent, "Распределение по полу")
            return
        
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = ['#93c572', '#78b478']
        
        labels = [f'Мужчины ({gender_count["Мужчины"]})', f'Женщины ({gender_count["Женщины"]})']
        sizes = [gender_count['Мужчины'], gender_count['Женщины']]
        
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels, 
            autopct='%1.1f%%',
            colors=colors, 
            startangle=90,
            textprops={'fontsize': 12, 'fontfamily': 'Georgia'}
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Распределение пациентов по полу', 
                    fontsize=14, fontfamily='Georgia', fontweight='bold', pad=20)
        
        self.embed_chart(parent, fig, "Распределение по полу")
    
    def create_age_chart(self, parent):
        ages = []
        for patient in self.patients:
            try:
                age = float(patient.get('age', 0))
                if 0 < age <= 120:
                    ages.append(age)
            except (ValueError, TypeError):
                continue
        
        if not ages:
            self.show_no_data_message(parent, "Распределение по возрасту")
            return
        
        fig, ax = plt.subplots(figsize=(8, 6))
        bins = min(10, len(set(ages)))
        n, bins, patches = ax.hist(ages, bins=bins, color='#93c572', alpha=0.7, 
                                 edgecolor='white', linewidth=1.2)
        
        ax.set_title('Распределение пациентов по возрасту', 
                    fontsize=14, fontfamily='Georgia', fontweight='bold', pad=20)
        ax.set_xlabel('Возраст', fontfamily='Georgia', fontsize=12)
        ax.set_ylabel('Количество пациентов', fontfamily='Georgia', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        self.embed_chart(parent, fig, "Распределение по возрасту")
    
    def create_bmi_gender_chart(self, parent):
        bmi_data = {'Мужчины': [], 'Женщины': []}
        
        for patient in self.patients:
            try:
                bmi = self.calculate_bmi(patient.get('weight', 0), patient.get('height', 0))
                if not math.isnan(bmi):
                    gender_str = str(patient.get('gender', '')).lower().strip()
                    
                    if any(word in gender_str for word in ['м', 'муж', 'male', 'мужской', 'мужчина']):
                        bmi_data['Мужчины'].append(bmi)
                    elif any(word in gender_str for word in ['ж', 'жен', 'female', 'женский', 'женщина']):
                        bmi_data['Женщины'].append(bmi)
            except (ValueError, TypeError):
                continue
        
        if not bmi_data['Мужчины'] and not bmi_data['Женщины']:
            self.show_no_data_message(parent, "ИМТ по полу")
            return
        
        fig, ax = plt.subplots(figsize=(8, 6))
        data = []
        labels = []
        colors = []
        
        if bmi_data['Мужчины']:
            data.append(bmi_data['Мужчины'])
            labels.append('Мужчины')
            colors.append('#93c572')
        
        if bmi_data['Женщины']:
            data.append(bmi_data['Женщины'])
            labels.append('Женщины')
            colors.append('#78b478')
        
        if data:
            box_plot = ax.boxplot(data, labels=labels, patch_artist=True)
            for patch, color in zip(box_plot['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            
            ax.set_title('Распределение ИМТ по полу', 
                        fontsize=14, fontfamily='Georgia', fontweight='bold', pad=20)
            ax.set_ylabel('ИМТ', fontfamily='Georgia', fontsize=12)
            ax.grid(True, alpha=0.3)
            
            self.embed_chart(parent, fig, "ИМТ по полу")
        else:
            self.show_no_data_message(parent, "ИМТ по полу")
    
    def create_bmi_age_chart(self, parent):
        ages = []
        bmis = []
        
        for patient in self.patients:
            try:
                age = float(patient.get('age', 0))
                bmi = self.calculate_bmi(patient.get('weight', 0), patient.get('height', 0))
                
                if 0 < age <= 120 and not math.isnan(bmi):
                    ages.append(age)
                    bmis.append(bmi)
            except (ValueError, TypeError):
                continue
        
        if len(ages) < 2:
            self.show_no_data_message(parent, "ИМТ от возраста")
            return
        
        fig, ax = plt.subplots(figsize=(8, 6))
        scatter = ax.scatter(ages, bmis, color='#93c572', alpha=0.6, s=60)
        
        if len(ages) > 1:
            try:
                z = np.polyfit(ages, bmis, 1)
                p = np.poly1d(z)
                ax.plot(ages, p(ages), color='#d2a679', linestyle='--', alpha=0.8, linewidth=2)
            except:
                pass
        
        ax.set_title('Зависимость ИМТ от возраста', 
                    fontsize=14, fontfamily='Georgia', fontweight='bold', pad=20)
        ax.set_xlabel('Возраст', fontfamily='Georgia', fontsize=12)
        ax.set_ylabel('ИМТ', fontfamily='Georgia', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        self.embed_chart(parent, fig, "ИМТ от возраста")
    
    def show_no_data_message(self, parent, chart_name):
        no_data_frame = ttk.Frame(parent, style='Modern.TFrame')
        no_data_frame.pack(fill='x', pady=10, padx=20)
        ttk.Label(no_data_frame, 
                 text=f"{chart_name} - недостаточно данных", 
                 style='Subtitle.TLabel',
                 foreground=TEXT_SECONDARY).pack()
    
    def embed_chart(self, parent, fig, title):
        chart_frame = ttk.Frame(parent, style='Modern.TFrame')
        chart_frame.pack(fill='x', pady=10, padx=20)
        ttk.Label(chart_frame, 
                 text=title, 
                 style='Subtitle.TLabel').pack(anchor='w', pady=(0, 10))
        try:
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill='x', padx=10)
            self.chart_canvases.append(canvas)
        except Exception as e:
            print(f"Ошибка встраивания графика {title}: {e}")
            ttk.Label(chart_frame, 
                     text=f"Ошибка отображения графика: {str(e)}", 
                     foreground='red').pack()
    
    def load_patients(self):
        if os.path.exists(self.patients_file):
            try:
                with open(self.patients_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки данных: {e}")
        return []

def main():
    root = tk.Tk()
    app = MedicalApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
