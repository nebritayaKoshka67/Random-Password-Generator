import random
import string
import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import scrolledtext

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # История паролей
        self.history_file = "password_history.json"
        self.password_history = self.load_history()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление отображения длины
        self.update_length_label()
        
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Генератор случайных паролей", 
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=10)
        
        # Фрейм для настроек
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки пароля", padding="10")
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        settings_frame.columnconfigure(1, weight=1)
        
        # Длина пароля
        ttk.Label(settings_frame, text="Длина пароля:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Фрейм для ползунка и значения
        length_frame = ttk.Frame(settings_frame)
        length_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        length_frame.columnconfigure(0, weight=1)
        
        self.length_var = tk.IntVar(value=12)
        self.length_slider = ttk.Scale(length_frame, from_=4, to=32, orient=tk.HORIZONTAL,
                                       variable=self.length_var, command=self.update_length_label)
        self.length_slider.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.length_label = ttk.Label(length_frame, text="", width=5)
        self.length_label.grid(row=0, column=1)
        
        # Настройка символов
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_special = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(settings_frame, text="Использовать цифры (0-9)", 
                       variable=self.use_digits).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Checkbutton(settings_frame, text="Использовать буквы (A-Z, a-z)", 
                       variable=self.use_letters).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Checkbutton(settings_frame, text="Использовать специальные символы (!@#$%^&*)", 
                       variable=self.use_special).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Кнопка генерации
        self.generate_btn = ttk.Button(settings_frame, text="Сгенерировать пароль", 
                                       command=self.generate_password)
        self.generate_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Отображение сгенерированного пароля
        password_frame = ttk.LabelFrame(main_frame, text="Сгенерированный пароль", padding="10")
        password_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        password_frame.columnconfigure(0, weight=1)
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, 
                                        font=('Courier', 12), state='readonly')
        self.password_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.copy_btn = ttk.Button(password_frame, text="Копировать", command=self.copy_to_clipboard)
        self.copy_btn.grid(row=0, column=1)
        
        # История паролей
        history_frame = ttk.LabelFrame(main_frame, text="История паролей", padding="10")
        history_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Создание Treeview для истории
        columns = ("Дата и время", "Пароль", "Длина")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=8)
        
        # Настройка колонок
        self.history_tree.heading("Дата и время", text="Дата и время")
        self.history_tree.heading("Пароль", text="Пароль")
        self.history_tree.heading("Длина", text="Длина")
        
        self.history_tree.column("Дата и время", width=150)
        self.history_tree.column("Пароль", width=300)
        self.history_tree.column("Длина", width=80)
        
        # Скроллбар для Treeview
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Кнопки для истории
        history_buttons_frame = ttk.Frame(history_frame)
        history_buttons_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(history_buttons_frame, text="Очистить историю", 
                  command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(history_buttons_frame, text="Сохранить историю", 
                  command=self.save_history_to_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(history_buttons_frame, text="Загрузить историю", 
                  command=self.load_history_from_file).pack(side=tk.LEFT, padx=5)
        
        # Загрузка истории в Treeview
        self.refresh_history_display()
        
    def update_length_label(self, event=None):
        """Обновление отображения длины пароля"""
        length = int(self.length_var.get())
        self.length_label.config(text=str(length))
        
    def generate_password(self):
        """Генерация случайного пароля"""
        length = int(self.length_var.get())
        
        # Проверка валидности
        if length < 4:
            messagebox.showerror("Ошибка", "Минимальная длина пароля - 4 символа")
            return
        if length > 32:
            messagebox.showerror("Ошибка", "Максимальная длина пароля - 32 символа")
            return
            
        # Сбор доступных символов
        characters = ""
        if self.use_digits.get():
            characters += string.digits
        if self.use_letters.get():
            characters += string.ascii_letters
        if self.use_special.get():
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            
        # Проверка, что выбран хотя бы один тип символов
        if not characters:
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов")
            return
            
        # Генерация пароля
        password = ''.join(random.choice(characters) for _ in range(length))
        
        # Отображение пароля
        self.password_var.set(password)
        
        # Сохранение в историю
        self.save_to_history(password, length)
        
        # Индикация успешной генерации
        self.generate_btn.config(text="Сгенерировано!", state='disabled')
        self.root.after(2000, lambda: self.generate_btn.config(text="Сгенерировать пароль", state='normal'))
        
    def save_to_history(self, password, length):
        """Сохранение пароля в историю"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "password": password,
            "length": length
        }
        self.password_history.append(entry)
        self.refresh_history_display()
        
    def refresh_history_display(self):
        """Обновление отображения истории"""
        # Очистка текущих данных
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        # Добавление новых данных
        for entry in self.password_history:
            self.history_tree.insert("", tk.END, values=(entry["timestamp"], 
                                                        entry["password"], 
                                                        entry["length"]))
            
    def copy_to_clipboard(self):
        """Копирование пароля в буфер обмена"""
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Предупреждение", "Нет пароля для копирования")
            
    def load_history(self):
        """Загрузка истории из файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
        
    def save_history_to_file(self):
        """Сохранение истории в файл"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.password_history, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", f"История сохранена в файл {self.history_file}")
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")
            
    def load_history_from_file(self):
        """Загрузка истории из файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.password_history = json.load(f)
                self.refresh_history_display()
                messagebox.showinfo("Успех", "История успешно загружена")
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Файл истории не найден")
            
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.password_history = []
            self.refresh_history_display()
            messagebox.showinfo("Успех", "История очищена")

def main():
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()


import json
import tkinter as tk
from tkinter import messagebox

def create_json_gui():
    root = tk.Tk()
    root.title("Создатель JSON файла")
    root.geometry("400x300")
    
    def create_empty_json():
        with open('password_history.json', 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Успех", "Пустой JSON файл создан!")
        root.destroy()
    
    def create_sample_json():
        sample = [
            {
                "timestamp": "2024-01-15 10:00:00",
                "password": "ExamplePass123!",
                "length": 14
            }
        ]
        with open('password_history.json', 'w', encoding='utf-8') as f:
            json.dump(sample, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Успех", "Пример JSON файла создан!")
        root.destroy()
    
    tk.Label(root, text="Создание JSON файла для генератора паролей", 
             font=('Arial', 12, 'bold')).pack(pady=20)
    
    tk.Button(root, text="Создать пустой JSON", 
              command=create_empty_json, width=30, height=2).pack(pady=10)
    
    tk.Button(root, text="Создать JSON с примером", 
              command=create_sample_json, width=30, height=2).pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    create_json_gui()
