import sys
import os
from datetime import datetime
import glob
import pandas as pd
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QDateEdit,
    QProgressBar,
    QScrollArea,
    QTabWidget,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from data_processor import data_processor
from data_analysis import DataAnalyzer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.analyzer = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Анализ временных рядов - Курсы INR")
        self.setGeometry(100, 100, 1200, 900)

        # Создаем центральный виджет с вкладками
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Создаем вкладки
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Вкладка 1: Основной функционал
        self.setup_basic_tab()

        # Вкладка 2: Расширенный анализ
        self.setup_analysis_tab()

        self.setCentralWidget(central_widget)

        # Обновляем статус кнопок
        self.update_buttons_state()

        # Начальное сообщение
        self.log_message("🚀 Приложение запущено. Выберите папку с данными.")

    def setup_basic_tab(self):
        """Вкладка с основным функционалом из лабы 2"""
        basic_tab = QWidget()
        layout = QVBoxLayout()

        # Прокручиваемая область для основного функционала
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_content.setLayout(scroll_layout)

        # 1. Выбор папки с данными
        folder_group = QGroupBox("1. Выбор папки с данными")
        folder_layout = QVBoxLayout()

        folder_btn_layout = QHBoxLayout()
        self.folder_path_label = QLabel("Папка не выбрана")
        self.folder_path_label.setStyleSheet(
            "QLabel { padding: 5px; border: 1px solid gray; }"
        )
        self.select_folder_btn = QPushButton("Выбрать папку")
        self.select_folder_btn.clicked.connect(self.select_folder)

        folder_btn_layout.addWidget(self.folder_path_label, 4)
        folder_btn_layout.addWidget(self.select_folder_btn, 1)
        folder_layout.addLayout(folder_btn_layout)

        folder_group.setLayout(folder_layout)
        scroll_layout.addWidget(folder_group)

        # 2. Поиск по дате
        search_group = QGroupBox("2. Поиск данных по дате")
        search_layout = QVBoxLayout()

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Дата:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(self.date_edit)

        self.search_btn = QPushButton("Получить данные")
        self.search_btn.clicked.connect(self.search_data)
        date_layout.addWidget(self.search_btn)

        search_layout.addLayout(date_layout)

        self.result_label = QLabel("Результат: -")
        self.result_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; color: #2E8B57; padding: 10px;"
        )
        search_layout.addWidget(self.result_label)

        search_group.setLayout(search_layout)
        scroll_layout.addWidget(search_group)

        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Версия поиска:"))

        self.search_version = QComboBox()
        self.search_version.addItems(
            [
                "Версия 0 - Единый файл",
                "Версия 1 - X/Y файлы",
                "Версия 2 - По годам",
                "Версия 3 - По неделям",
            ]
        )
        version_layout.addWidget(self.search_version)

        search_layout.addLayout(version_layout)

        demo_search_btn = QPushButton("Демо: 4 версии поиска")
        demo_search_btn.clicked.connect(self.demo_search_versions_ui)
        search_layout.addWidget(demo_search_btn)

        # 3. Создание аннотации
        annotation_group = QGroupBox("3. Создание аннотации")
        annotation_layout = QVBoxLayout()

        annotation_btn_layout = QHBoxLayout()
        self.create_annotation_btn = QPushButton("Создать аннотацию исходного датасета")
        self.create_annotation_btn.clicked.connect(self.create_annotation)
        annotation_btn_layout.addWidget(self.create_annotation_btn)

        annotation_layout.addLayout(annotation_btn_layout)
        annotation_group.setLayout(annotation_layout)
        scroll_layout.addWidget(annotation_group)

        # 4. Реорганизация данных
        reorganize_group = QGroupBox("4. Реорганизация данных")
        reorganize_layout = QVBoxLayout()

        buttons_layout = QHBoxLayout()

        self.split_xy_btn = QPushButton("Разделить на X/Y")
        self.split_xy_btn.clicked.connect(lambda: self.reorganize_data("xy"))
        buttons_layout.addWidget(self.split_xy_btn)

        self.split_years_btn = QPushButton("Разделить по годам")
        self.split_years_btn.clicked.connect(lambda: self.reorganize_data("years"))
        buttons_layout.addWidget(self.split_years_btn)

        self.split_weeks_btn = QPushButton("Разделить по неделям")
        self.split_weeks_btn.clicked.connect(lambda: self.reorganize_data("weeks"))
        buttons_layout.addWidget(self.split_weeks_btn)

        reorganize_layout.addLayout(buttons_layout)

        annotation_reorg_layout = QHBoxLayout()
        self.create_reorg_annotation_btn = QPushButton(
            "Создать аннотацию реорганизованных данных"
        )
        self.create_reorg_annotation_btn.clicked.connect(
            self.create_reorganized_annotation
        )
        annotation_reorg_layout.addWidget(self.create_reorg_annotation_btn)

        reorganize_layout.addLayout(annotation_reorg_layout)
        reorganize_group.setLayout(reorganize_layout)
        scroll_layout.addWidget(reorganize_group)

        # 5. Загрузка новых данных
        download_group = QGroupBox("5. Загрузка новых данных")
        download_layout = QVBoxLayout()

        self.download_btn = QPushButton("Загрузить новые данные с ЦБ РФ")
        self.download_btn.clicked.connect(self.download_new_data)
        download_layout.addWidget(self.download_btn)

        download_group.setLayout(download_layout)
        scroll_layout.addWidget(download_group)

        download_dates_layout = QHBoxLayout()
        download_dates_layout.addWidget(QLabel("С:"))
        self.download_start_date = QDateEdit()
        self.download_start_date.setDate(QDate(2016, 1, 1))
        self.download_start_date.setDisplayFormat("yyyy-MM-dd")
        download_dates_layout.addWidget(self.download_start_date)

        download_dates_layout.addWidget(QLabel("По:"))
        self.download_end_date = QDateEdit()
        self.download_end_date.setDate(QDate.currentDate())
        self.download_end_date.setDisplayFormat("yyyy-MM-dd")
        download_dates_layout.addWidget(self.download_end_date)

        download_layout.addLayout(download_dates_layout)

        # 6. Лог действий
        log_group = QGroupBox("Лог действий")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)

        log_group.setLayout(log_layout)
        scroll_layout.addWidget(log_group)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        basic_tab.setLayout(layout)
        self.tabs.addTab(basic_tab, "Основной функционал")

    def setup_analysis_tab(self):
        """Вкладка расширенного анализа данных"""
        analysis_tab = QWidget()
        layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_content.setLayout(scroll_layout)

        # 1. Инициализация анализатора
        init_group = QGroupBox("1. Инициализация анализатора данных")
        init_layout = QVBoxLayout()

        self.init_analyzer_btn = QPushButton("Инициализировать анализатор данных")
        self.init_analyzer_btn.clicked.connect(self.initialize_analyzer)
        init_layout.addWidget(self.init_analyzer_btn)

        self.analyzer_status = QLabel("Статус: Не инициализирован")
        init_layout.addWidget(self.analyzer_status)

        init_group.setLayout(init_layout)
        scroll_layout.addWidget(init_group)

        # 2. Базовый анализ
        basic_analysis_group = QGroupBox("2. Базовый анализ данных")
        basic_layout = QVBoxLayout()

        analysis_buttons_layout = QHBoxLayout()

        self.missing_btn = QPushButton("Проверить пропущенные значения")
        self.missing_btn.clicked.connect(self.check_missing_values)
        analysis_buttons_layout.addWidget(self.missing_btn)

        self.deviation_btn = QPushButton("Добавить столбцы отклонений")
        self.deviation_btn.clicked.connect(self.add_deviation_columns)
        analysis_buttons_layout.addWidget(self.deviation_btn)

        self.stats_btn = QPushButton("Рассчитать статистики")
        self.stats_btn.clicked.connect(self.calculate_statistics)
        analysis_buttons_layout.addWidget(self.stats_btn)

        basic_layout.addLayout(analysis_buttons_layout)
        basic_analysis_group.setLayout(basic_layout)
        scroll_layout.addWidget(basic_analysis_group)

        # 3. Фильтрация данных
        filter_group = QGroupBox("3. Фильтрация данных")
        filter_layout = QVBoxLayout()

        # Фильтрация по отклонению
        deviation_layout = QHBoxLayout()
        deviation_layout.addWidget(QLabel("Порог отклонения:"))
        self.deviation_input = QLineEdit()
        self.deviation_input.setText("0.5")
        self.deviation_input.setPlaceholderText("Введите значение отклонения")
        deviation_layout.addWidget(self.deviation_input)

        self.filter_deviation_btn = QPushButton("Фильтровать по отклонению")
        self.filter_deviation_btn.clicked.connect(self.filter_by_deviation)
        deviation_layout.addWidget(self.filter_deviation_btn)

        filter_layout.addLayout(deviation_layout)

        # Фильтрация по дате
        date_filter_layout = QHBoxLayout()
        date_filter_layout.addWidget(QLabel("Начальная дата:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate(2020, 1, 1))
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        date_filter_layout.addWidget(self.start_date_edit)

        date_filter_layout.addWidget(QLabel("Конечная дата:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate(2020, 12, 31))
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        date_filter_layout.addWidget(self.end_date_edit)

        self.filter_date_btn = QPushButton("Фильтровать по дате")
        self.filter_date_btn.clicked.connect(self.filter_by_date_range)
        date_filter_layout.addWidget(self.filter_date_btn)

        filter_layout.addLayout(date_filter_layout)
        filter_group.setLayout(filter_layout)
        scroll_layout.addWidget(filter_group)

        # 4. Группировка данных
        group_group = QGroupBox("4. Группировка данных")
        group_layout = QVBoxLayout()

        self.group_month_btn = QPushButton("Группировать по месяцам")
        self.group_month_btn.clicked.connect(self.group_by_month)
        group_layout.addWidget(self.group_month_btn)

        group_group.setLayout(group_layout)
        scroll_layout.addWidget(group_group)

        # 5. Визуализация
        viz_group = QGroupBox("5. Визуализация данных")
        viz_layout = QVBoxLayout()

        plot_buttons_layout = QHBoxLayout()

        self.plot_full_btn = QPushButton("График за весь период")
        self.plot_full_btn.clicked.connect(self.plot_full_period)
        plot_buttons_layout.addWidget(self.plot_full_btn)

        self.plot_month_btn = QPushButton("График за месяц")
        self.plot_month_btn.clicked.connect(self.plot_monthly_analysis)
        plot_buttons_layout.addWidget(self.plot_month_btn)

        viz_layout.addLayout(plot_buttons_layout)

        # Поле для ввода месяца
        month_layout = QHBoxLayout()
        month_layout.addWidget(QLabel("Месяц (ГГГГ-ММ):"))
        self.month_input = QLineEdit()
        self.month_input.setText("2020-01")
        self.month_input.setPlaceholderText("2020-01")
        month_layout.addWidget(self.month_input)

        viz_layout.addLayout(month_layout)
        viz_group.setLayout(viz_layout)
        scroll_layout.addWidget(viz_group)

        # Лог анализа
        analysis_log_group = QGroupBox("Лог анализа")
        analysis_log_layout = QVBoxLayout()

        self.analysis_log = QTextEdit()
        self.analysis_log.setReadOnly(True)
        self.analysis_log.setMaximumHeight(200)
        analysis_log_layout.addWidget(self.analysis_log)

        analysis_log_group.setLayout(analysis_log_layout)
        scroll_layout.addWidget(analysis_log_group)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        analysis_tab.setLayout(layout)
        self.tabs.addTab(analysis_tab, "Расширенный анализ")

    def _get_data_xy_files(self, date: datetime):
        """Версия 1: поиск в раздельных файлах"""
        try:
            dates_df = pd.read_csv(os.path.join(data_processor.dataset_path, "X.csv"))
            data_df = pd.read_csv(os.path.join(data_processor.dataset_path, "Y.csv"))
            dates_df["Date"] = pd.to_datetime(dates_df["Date"])
            mask = dates_df["Date"] == date
            if mask.any():
                idx = mask.idxmax()
                return data_df.iloc[idx]["INR_Rate"]
            return None
        except Exception:
            return None

    def _get_data_year_files(self, date: datetime):
        """Версия 2: поиск в файлах по годам"""
        try:
            year = date.year
            files = glob.glob(os.path.join(data_processor.dataset_path, f"{year}*.csv"))
            for file in files:
                if any(
                    excluded in file for excluded in ["X.csv", "Y.csv", "dataset.csv"]
                ):
                    continue
                df = pd.read_csv(file)
                df["Date"] = pd.to_datetime(df["Date"])
                mask = df["Date"] == date
                result_df = df[mask]
                if not result_df.empty:
                    return result_df["INR_Rate"].iloc[0]
            return None
        except Exception:
            return None

    def _get_data_week_files(self, date: datetime):
        """Версия 3: поиск в файлах по неделям"""
        try:
            files = glob.glob(os.path.join(data_processor.dataset_path, "*_*.csv"))
            for file in files:
                if any(
                    excluded in file for excluded in ["X.csv", "Y.csv", "dataset.csv"]
                ):
                    continue
                df = pd.read_csv(file)
                df["Date"] = pd.to_datetime(df["Date"])
                mask = df["Date"] == date
                result_df = df[mask]
                if not result_df.empty:
                    return result_df["INR_Rate"].iloc[0]
            return None
        except Exception:
            return None

    # === МЕТОДЫ ОСНОВНОГО ФУНКЦИОНАЛА ===

    def select_folder(self):
        """Выбор папки с данными"""
        folderpath = QFileDialog.getExistingDirectory(self, "Выберите папку с данными")
        if folderpath:
            self.folder_path_label.setText(folderpath)
            success = data_processor.set_dataset_path(folderpath)
            if success:
                record_count = len(data_processor.current_dataset)
                date_range = f"{data_processor.current_dataset['Date'].min().strftime('%Y-%m-%d')} - {data_processor.current_dataset['Date'].max().strftime('%Y-%m-%d')}"

                self.log_message(f"📁 Папка выбрана: {folderpath}")
                self.log_message(f"📊 Загружено записей: {record_count}")
                self.log_message(f"📅 Диапазон дат: {date_range}")
                # Автоматически инициализируем анализатор
                self.initialize_analyzer()
            else:
                self.log_message(
                    " В выбранной папке нет dataset.csv или ошибка загрузки"
                )

            self.update_buttons_state()

    def search_data(self):
        """Поиск данных по дате с выбранной версией"""
        if data_processor.current_dataset is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите папку с данными!")
            return

        selected_date = self.date_edit.date().toPython()
        version_index = self.search_version.currentIndex()

        rate = None
        version_name = ""

        # Выбор версии поиска
        if version_index == 0:  # Единый файл
            rate = data_processor.get_data_by_date(selected_date)
            version_name = "единый файл"
        elif version_index == 1:  # X/Y файлы
            rate = self._get_data_xy_files(selected_date)
            version_name = "X/Y файлы"
        elif version_index == 2:  # По годам
            rate = self._get_data_year_files(selected_date)
            version_name = "по годам"
        elif version_index == 3:  # По неделям
            rate = self._get_data_week_files(selected_date)
            version_name = "по неделям"

        if rate is not None:
            self.result_label.setText(f"Результат: {rate:.4f} RUB ({version_name})")
            self.result_label.setStyleSheet(
                "font-weight: bold; font-size: 14px; color: #2E8B57; padding: 10px;"
            )
            self.log_message(
                f"🔍 Найдено для {selected_date.strftime('%Y-%m-%d')}: {rate:.4f} RUB ({version_name})"
            )
        else:
            self.result_label.setText(f"Результат: данные не найдены ({version_name})")
            self.result_label.setStyleSheet(
                "font-weight: bold; font-size: 14px; color: #DC143C; padding: 10px;"
            )
            self.log_message(
                f"❌ Данные для {selected_date.strftime('%Y-%m-%d')} не найдены ({version_name})"
            )

    def create_annotation(self):
        """Создание аннотации исходного датасета"""
        if data_processor.current_dataset is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите папку с данными!")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить аннотацию", "annotation.txt", "Text files (*.txt)"
        )
        if filepath:
            result = data_processor.create_annotation(filepath, "original")
            if "error" in result:
                QMessageBox.critical(self, "Ошибка", result["error"])
                self.log_message(f"❌ {result['error']}")
            else:
                QMessageBox.information(self, "Успех", result["message"])
                self.log_message(f"📄 {result['message']}")

    def reorganize_data(self, data_type):
        """Реорганизация данных"""
        if data_processor.current_dataset is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите папку с данными!")
            return

        folderpath = QFileDialog.getExistingDirectory(
            self, "Выберите папку для сохранения"
        )
        if folderpath:
            if data_type == "xy":
                result = data_processor.split_to_xy(folderpath)
            elif data_type == "years":
                result = data_processor.split_by_years(folderpath)
            elif data_type == "weeks":
                result = data_processor.split_by_weeks(folderpath)

            if "error" in result:
                QMessageBox.critical(self, "Ошибка", result["error"])
                self.log_message(f"❌ {result['error']}")
            else:
                QMessageBox.information(self, "Успех", result["message"])
                self.log_message(f"✅ {result['message']}")
                if "files" in result:
                    for file in result["files"]:
                        self.log_message(f"   📁 {file}")

    def create_reorganized_annotation(self):
        """Создание аннотации для реорганизованных данных"""
        if data_processor.current_dataset is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите папку с данными!")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить аннотацию",
            "annotation_reorganized.txt",
            "Text files (*.txt)",
        )
        if filepath:
            data_type = "original"
            dataset_path = data_processor.dataset_path

            if os.path.exists(os.path.join(dataset_path, "X.csv")):
                data_type = "xy"
            elif any(
                f.endswith(".csv") and f not in ["X.csv", "Y.csv", "dataset.csv"]
                for f in os.listdir(dataset_path)
            ):
                csv_files = [
                    f
                    for f in os.listdir(dataset_path)
                    if f.endswith(".csv") and f not in ["X.csv", "Y.csv", "dataset.csv"]
                ]
                if csv_files:
                    data_type = "years"

            result = data_processor.create_annotation(filepath, data_type)
            if "error" in result:
                QMessageBox.critical(self, "Ошибка", result["error"])
                self.log_message(f" {result['error']}")
            else:
                QMessageBox.information(self, "Успех", result["message"])
                self.log_message(f"📄 {result['message']}")

    def download_new_data(self):
        """Загрузка новых данных с ЦБ РФ с ограничением по датам"""
        if data_processor.dataset_path is None:
            QMessageBox.warning(
                self, "Ошибка", "Сначала выберите папку для сохранения данных!"
            )
            return

        # Получаем выбранные даты
        start_date = self.download_start_date.date().toPython()
        end_date = self.download_end_date.date().toPython()

        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Загрузить данные с {start_date.strftime('%Y-%m-%d')} по {end_date.strftime('%Y-%m-%d')}?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.log_message(
                f" Загрузка данных с {start_date.strftime('%Y-%m-%d')} по {end_date.strftime('%Y-%m-%d')}..."
            )
            result = data_processor.download_new_data(start_date, end_date)

            if "error" in result:
                QMessageBox.critical(self, "Ошибка", result["error"])
                self.log_message(f" {result['error']}")
            else:
                QMessageBox.information(self, "Успех", result["message"])
                self.log_message(f" {result['message']}")
                self.update_buttons_state()

    def demo_search_versions_ui(self):
        """Демонстрация 4 версий поиска через интерфейс"""
        if data_processor.current_dataset is None:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите папку с данными!")
            return

        selected_date = self.date_edit.date().toPython()
        results = []

        # Версия 0: единый файл
        result0 = data_processor.get_data_by_date(selected_date)
        results.append(f"Версия 0: {result0}")

        # Версия 1: X/Y файлы
        result1 = self._get_data_xy_files(selected_date)
        results.append(f"Версия 1: {result1}")

        # Версия 2: по годам
        result2 = self._get_data_year_files(selected_date)
        results.append(f"Версия 2: {result2}")

        # Версия 3: по неделям
        result3 = self._get_data_week_files(selected_date)
        results.append(f"Версия 3: {result3}")

        # Показываем результаты
        message = (
            f"Результаты поиска для {selected_date.strftime('%Y-%m-%d')}:\n"
            + "\n".join(results)
        )
        QMessageBox.information(self, "4 версии поиска", message)

    # === МЕТОДЫ РАСШИРЕННОГО АНАЛИЗА ===

    def initialize_analyzer(self):
        """Инициализация анализатора данных"""
        try:
            if data_processor.current_dataset is not None:
                self.analyzer = DataAnalyzer(data_processor)
                self.analyzer_status.setText("Статус: Инициализирован успешно")
                self.analyzer_status.setStyleSheet("color: green; font-weight: bold;")
                self.log_analysis(" Анализатор данных инициализирован успешно")
                self.update_analysis_buttons(True)
            else:
                self.analyzer_status.setText("Статус: Данные не загружены")
                self.analyzer_status.setStyleSheet("color: red; font-weight: bold;")
                self.log_analysis(
                    " Не удалось инициализировать анализатор: данные не загружены"
                )
        except Exception as e:
            self.analyzer_status.setText(f"Статус: Ошибка инициализации")
            self.log_analysis(f" Ошибка инициализации анализатора: {str(e)}")

    def check_missing_values(self):
        """Проверка пропущенных значений"""
        if not self.check_analyzer():
            return

        try:
            missing_stats = self.analyzer.check_missing_values()
            self.log_analysis(" Проверка пропущенных значений завершена")
        except Exception as e:
            self.log_analysis(f" Ошибка проверки пропущенных значений: {str(e)}")

    def add_deviation_columns(self):
        """Добавление столбцов с отклонениями"""
        if not self.check_analyzer():
            return

        try:
            self.analyzer.add_deviation_columns()
            self.log_analysis(" Столбцы с отклонениями добавлены")
        except Exception as e:
            self.log_analysis(f" Ошибка добавления столбцов: {str(e)}")

    def calculate_statistics(self):
        """Расчет статистик"""
        if not self.check_analyzer():
            return

        try:
            stats = self.analyzer.calculate_statistics()
            self.log_analysis(" Статистики рассчитаны")
        except Exception as e:
            self.log_analysis(f" Ошибка расчета статистик: {str(e)}")

    def filter_by_deviation(self):
        """Фильтрация по отклонению"""
        if not self.check_analyzer():
            return

        try:
            threshold = float(self.deviation_input.text())
            filtered_df = self.analyzer.filter_by_deviation(threshold)
            self.log_analysis(f" Фильтрация по отклонению >= {threshold} завершена")
            self.log_analysis(f"   Найдено записей: {len(filtered_df)}")
        except ValueError:
            self.log_analysis(
                " Ошибка: введите числовое значение для порога отклонения"
            )
        except Exception as e:
            self.log_analysis(f" Ошибка фильтрации: {str(e)}")

    def filter_by_date_range(self):
        """Фильтрация по дате"""
        if not self.check_analyzer():
            return

        try:
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

            filtered_df = self.analyzer.filter_by_date_range(start_date, end_date)
            self.log_analysis(
                f" Фильтрация по датам {start_date} - {end_date} завершена"
            )
            self.log_analysis(f"   Найдено записей: {len(filtered_df)}")
        except Exception as e:
            self.log_analysis(f" Ошибка фильтрации по дате: {str(e)}")

    def group_by_month(self):
        """Группировка по месяцам"""
        if not self.check_analyzer():
            return

        try:
            monthly_data = self.analyzer.group_by_month()
            self.log_analysis(" Группировка по месяцам завершена")
            self.log_analysis(f"   Сгруппировано месяцев: {len(monthly_data)}")
        except Exception as e:
            self.log_analysis(f" Ошибка группировки: {str(e)}")

    def plot_full_period(self):
        if not self.check_analyzer():
            return

        # ДЛЯ ОТЛАДКИ - проверим откуда данные
        print(
            f"Диапазон дат в анализаторе: {self.analyzer.df['date'].min()} - {self.analyzer.df['date'].max()}"
        )
        print(f"Количество записей: {len(self.analyzer.df)}")
        try:
            self.analyzer.plot_full_period()
            self.log_analysis(" График за весь период построен")
        except Exception as e:
            self.log_analysis(f" Ошибка построения графика: {str(e)}")

    def plot_monthly_analysis(self):
        """Построение графика за месяц"""
        if not self.check_analyzer():
            return

        try:
            month_str = self.month_input.text()
            self.analyzer.plot_monthly_analysis(month_str)
            self.log_analysis(f" График за месяц {month_str} построен")
        except Exception as e:
            self.log_analysis(f" Ошибка построения графика за месяц: {str(e)}")

    def check_analyzer(self):
        """Проверка инициализации анализатора"""
        if self.analyzer is None or self.analyzer.df is None:
            QMessageBox.warning(
                self, "Ошибка", "Сначала инициализируйте анализатор данных!"
            )
            return False
        return True

    # === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===

    def log_message(self, message):
        """Добавить сообщение в лог основного функционала"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def log_analysis(self, message):
        """Добавить сообщение в лог анализа"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.analysis_log.append(f"[{timestamp}] {message}")
        self.analysis_log.verticalScrollBar().setValue(
            self.analysis_log.verticalScrollBar().maximum()
        )

    def update_buttons_state(self):
        """Обновить состояние кнопок основного функционала"""
        has_data = data_processor.current_dataset is not None
        has_folder = data_processor.dataset_path is not None

        self.search_btn.setEnabled(has_data)
        self.create_annotation_btn.setEnabled(has_data)
        self.split_xy_btn.setEnabled(has_data)
        self.split_years_btn.setEnabled(has_data)
        self.split_weeks_btn.setEnabled(has_data)
        self.create_reorg_annotation_btn.setEnabled(has_data)
        self.download_btn.setEnabled(has_folder)

        # Обновляем состояние кнопок анализа
        self.update_analysis_buttons(has_data)

    def update_analysis_buttons(self, enabled):
        """Обновить состояние кнопок анализа"""
        analysis_buttons = [
            self.init_analyzer_btn,
            self.missing_btn,
            self.deviation_btn,
            self.stats_btn,
            self.filter_deviation_btn,
            self.filter_date_btn,
            self.group_month_btn,
            self.plot_full_btn,
            self.plot_month_btn,
        ]

        for button in analysis_buttons:
            button.setEnabled(enabled)
