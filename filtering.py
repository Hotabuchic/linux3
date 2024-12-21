import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class LogAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализатор логов")

        self.file_path = None

        # Верхняя панель: Выбор файла
        file_frame = tk.Frame(root)
        file_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(file_frame, text="Выберите лог-файл:").pack(side="left")
        self.file_selector = ttk.Combobox(
            file_frame, values=["file_system_log.txt", "network_log.txt", "process_log.txt"]
        )
        self.file_selector.pack(side="left", padx=5)
        self.file_selector.bind("<<ComboboxSelected>>", self.load_file)

        # Панель фильтров (фильтр по пользователю)
        filter_frame = tk.Frame(root)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Фильтр по пользователю:").pack(side="left")
        self.user_entry = tk.Entry(filter_frame)
        self.user_entry.pack(side="left", padx=5)

        tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).pack(side="left", padx=5)

        # Панель фильтра по времени
        time_filter_frame = tk.Frame(root)
        time_filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(time_filter_frame, text="Начальное время (ГГГГ-ММ-ДД ЧЧ:ММ:СС):").pack(side="left")
        self.start_time_entry = tk.Entry(time_filter_frame)
        self.start_time_entry.pack(side="left", padx=5)

        tk.Label(time_filter_frame, text="Конечное время (ГГГГ-ММ-ДД ЧЧ:ММ:СС):").pack(side="left")
        self.end_time_entry = tk.Entry(time_filter_frame)
        self.end_time_entry.pack(side="left", padx=5)

        # Панель фильтра по ключевым словам
        keyword_filter_frame = tk.Frame(root)
        keyword_filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(keyword_filter_frame, text="Фильтр по ключевым словам:").pack(side="left")
        self.keyword_entry = tk.Entry(keyword_filter_frame)
        self.keyword_entry.pack(side="left", padx=5)

        tk.Button(keyword_filter_frame, text="Применить ключевой фильтр", command=self.apply_keyword_filter).pack(
            side="left", padx=5)

        # Панель поиска
        search_frame = tk.Frame(root)
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Поиск:").pack(side="left")
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side="left", padx=5)

        tk.Button(search_frame, text="Найти", command=self.search).pack(side="left", padx=5)

        # Панель вывода логов
        self.text_area = tk.Text(root, wrap="none", state="disabled")
        self.text_area.pack(fill="both", expand=True, padx=10, pady=5)

    def load_file(self, event=None):
        selected_file = self.file_selector.get()
        if selected_file:
            self.file_path = selected_file
            self.display_file_content()

    def display_file_content(self):
        if not self.file_path:
            return
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                content = file.read()
            self.text_area.config(state="normal")
            self.text_area.delete(1.0, "end")
            self.text_area.insert("end", content)
            self.text_area.config(state="disabled")
        except Exception as e:
            self.show_error(f"Ошибка при загрузке файла: {e}")

    def apply_filter(self):
        if not self.file_path:
            self.show_error("Сначала выберите файл.")
            return

        user_filter = self.user_entry.get().strip()
        start_time_str = self.start_time_entry.get().strip()
        end_time_str = self.end_time_entry.get().strip()
        filtered_lines = []

        # Попытка преобразовать введенные строки в datetime
        try:
            start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S") if start_time_str else None
            end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S") if end_time_str else None
        except ValueError:
            self.show_error("Неверный формат времени. Используйте ГГГГ-ММ-ДД ЧЧ:ММ:СС.")
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                for line in file:
                    parts = line.split(" - ")
                    if len(parts) < 3:
                        continue  # Если строка не содержит ожидаемого формата, пропускаем её

                    # Извлекаем временную метку и пользователя
                    timestamp_str = parts[0].strip()
                    user = parts[1].strip()

                    try:
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")
                    except ValueError:
                        continue  # Пропускаем строки с некорректным временем

                    # Проверяем временные рамки
                    if (start_time and timestamp < start_time) or (end_time and timestamp > end_time):
                        continue

                    # Проверяем пользователя
                    if user_filter and user_filter.lower() not in user.lower():
                        continue

                    filtered_lines.append(line)

            self.display_filtered_content(filtered_lines)
        except Exception as e:
            self.show_error(f"Ошибка при фильтрации: {e}")

    def apply_keyword_filter(self):
        if not self.file_path:
            self.show_error("Сначала выберите файл.")
            return

        keyword = self.keyword_entry.get().strip()
        if not keyword:
            self.show_error("Введите ключевое слово для фильтрации.")
            return

        filtered_lines = []
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                for line in file:
                    if keyword in line:
                        filtered_lines.append(line)

            self.display_filtered_content(filtered_lines)
        except Exception as e:
            self.show_error(f"Ошибка при фильтрации: {e}")

    def search(self):
        search_query = self.search_entry.get().strip()
        if not search_query:
            self.show_error("Введите строку для поиска.")
            return

        self.text_area.config(state="normal")
        self.text_area.delete(1.0, "end")

        if self.file_path:
            with open(self.file_path, "r", encoding="utf-8") as file:
                for line in file:
                    if search_query in line:
                        self.text_area.insert("end", line)
            self.text_area.config(state="disabled")
        else:
            self.show_error("Сначала загрузите лог-файл.")

    def display_filtered_content(self, lines):
        self.text_area.config(state="normal")
        self.text_area.delete(1.0, "end")
        self.text_area.insert("end", "".join(lines))
        self.text_area.config(state="disabled")

    def show_error(self, message):
        messagebox.showerror("Ошибка", message)


if __name__ == "__main__":
    root = tk.Tk()
    app = LogAnalyzerApp(root)
    root.mainloop()
