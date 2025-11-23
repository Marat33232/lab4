import glob
import os
import csv
import pandas as pd
from datetime import datetime, timedelta
import requests
from typing import Optional, Tuple, List, Dict
from data_analysis import DataAnalyzer


class DataProcessor:
    def __init__(self):
        self.dataset_path = None
        self.current_dataset = None

    def set_dataset_path(self, folder_path: str) -> bool:
        """Загрузка dataset.csv из указанной папки"""
        try:
            dataset_path = os.path.join(folder_path, "dataset.csv")
            if os.path.exists(dataset_path):
                self.current_dataset = pd.read_csv(dataset_path)
                self.current_dataset["Date"] = pd.to_datetime(
                    self.current_dataset["Date"]
                )
                self.dataset_path = folder_path
                print(f"Загружено {len(self.current_dataset)} записей")
                return True
            else:
                print(f"Файл dataset.csv не найден в папке {folder_path}")
                return False
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            return False

    def get_data_by_date(self, date: datetime) -> Optional[float]:
        if self.current_dataset is None:
            return None

        try:
            target_date = pd.Timestamp(date)
            mask = self.current_dataset["Date"] == target_date
            result_df = self.current_dataset[mask]

            if not result_df.empty:
                return result_df["INR_Rate"].iloc[0]
            else:
                return None
        except Exception as e:
            print(f"Ошибка поиска: {e}")
            return None

    def split_to_xy(self, output_path: str = None) -> Dict[str, str]:
        """Разделение на X.csv и Y.csv"""
        if self.current_dataset is None:
            return {"error": "Данные не загружены"}

        path = output_path if output_path else self.dataset_path

        try:
            self.current_dataset[["Date"]].to_csv(
                os.path.join(path, "X.csv"), index=False
            )
            self.current_dataset[["INR_Rate"]].to_csv(
                os.path.join(path, "Y.csv"), index=False
            )

            return {
                "success": True,
                "message": f"Созданы файлы X.csv и Y.csv в {path}",
                "files": ["X.csv", "Y.csv"],
            }
        except Exception as e:
            return {"error": f"Ошибка: {e}"}

    def split_by_years(self, output_path: str = None) -> Dict[str, str]:
        """Разделение по годам"""
        if self.current_dataset is None:
            return {"error": "Данные не загружены"}

        path = output_path if output_path else self.dataset_path

        try:
            df = self.current_dataset.copy()
            created_files = []

            for year, group in df.groupby(df["Date"].dt.year):
                if not group.empty:
                    start_date = group["Date"].min().strftime("%Y%m%d")
                    end_date = group["Date"].max().strftime("%Y%m%d")
                    filename = f"{start_date}_{end_date}.csv"
                    filepath = os.path.join(path, filename)

                    group.to_csv(filepath, index=False)
                    created_files.append(filename)

            return {
                "success": True,
                "message": f"Создано {len(created_files)} файлов по годам в {path}",
                "files": created_files,
            }
        except Exception as e:
            return {"error": f"Ошибка: {e}"}

    def split_by_weeks(self, output_path: str = None) -> Dict[str, str]:
        """Разделение по неделям"""
        if self.current_dataset is None:
            return {"error": "Данные не загружены"}

        path = output_path if output_path else self.dataset_path

        try:
            df = self.current_dataset.copy()
            created_files = []

            df["YearWeek"] = (
                df["Date"].dt.isocalendar().year.astype(str)
                + "-"
                + df["Date"].dt.isocalendar().week.astype(str).str.zfill(2)
            )

            for week, group in df.groupby("YearWeek"):
                if not group.empty:
                    start_date = group["Date"].min().strftime("%Y%m%d")
                    end_date = group["Date"].max().strftime("%Y%m%d")
                    filename = f"{start_date}_{end_date}.csv"
                    filepath = os.path.join(path, filename)

                    group[["Date", "INR_Rate"]].to_csv(filepath, index=False)
                    created_files.append(filename)

            return {
                "success": True,
                "message": f"Создано {len(created_files)} файлов по неделям в {path}",
                "files": created_files,
            }
        except Exception as e:
            return {"error": f"Ошибка: {e}"}

    def create_annotation(
        self, annotation_path: str, dataset_type: str = "original"
    ) -> Dict[str, str]:
        """Создание файла аннотации"""
        try:
            if not self.dataset_path:
                return {"error": "Путь к данным не установлен"}

            if dataset_type == "original":
                files = (
                    ["dataset.csv"]
                    if os.path.exists(os.path.join(self.dataset_path, "dataset.csv"))
                    else []
                )
            elif dataset_type == "xy":
                files = [
                    f
                    for f in ["X.csv", "Y.csv"]
                    if os.path.exists(os.path.join(self.dataset_path, f))
                ]
            elif dataset_type == "years":
                files = [
                    f
                    for f in os.listdir(self.dataset_path)
                    if f.endswith(".csv")
                    and f not in ["X.csv", "Y.csv", "dataset.csv"]
                    and len(f) == 16
                ]
            elif dataset_type == "weeks":
                files = [
                    f
                    for f in os.listdir(self.dataset_path)
                    if f.endswith(".csv")
                    and f not in ["X.csv", "Y.csv", "dataset.csv"]
                    and len(f) == 16
                ]
            else:
                files = []

            with open(annotation_path, "w", encoding="utf-8") as f:
                f.write(f"Аннотация датасета\n")
                f.write("=" * 50 + "\n")
                f.write(f"Тип организации: {dataset_type}\n")
                f.write(f"Путь к данным: {self.dataset_path}\n")
                f.write(f"Количество файлов: {len(files)}\n")
                f.write("Файлы:\n")
                for file in files:
                    file_path = os.path.join(self.dataset_path, file)
                    if os.path.exists(file_path):
                        df = pd.read_csv(file_path)
                        f.write(f"  - {file}: {len(df)} записей\n")
                    else:
                        f.write(f"  - {file}: файл не найден\n")
                f.write(f"\nСоздано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            return {
                "success": True,
                "message": f"Файл аннотации создан: {annotation_path}",
                "files": files,
                "dataset_type": dataset_type,
            }
        except Exception as e:
            return {"error": f"Ошибка создания аннотации: {e}"}

    def download_new_data(self, start_date=None, end_date=None) -> Dict[str, str]:
        """Скачать новые данные с ЦБ РФ с ограничением по датам"""
        try:
            if not self.dataset_path:
                return {"error": "Сначала выберите папку для сохранения данных"}

            print("Начинаем сбор данных по курсу индийской рупии (INR)...")

            # Используем переданные даты или значения по умолчанию
            if end_date is None:
                end_date = datetime.today()
            if start_date is None:
                start_date = datetime(2016, 1, 1)

            # Добавьте проверку, что start_date не позже end_date
            if start_date > end_date:
                return {"error": "Начальная дата не может быть позже конечной"}

            dates = self._generate_date_range(start_date, end_date)
            data = []

            for date_str in dates:
                rate = self._get_inr_rate(date_str)
                if rate is not None:
                    formatted_date = date_str.replace("/", "-")
                    data.append([formatted_date, rate])
                    print(f" {formatted_date}: {rate} RUB")
                else:
                    print(f"--- {date_str}: данные не найдены")

            dataset_path = os.path.join(self.dataset_path, "dataset.csv")

            with open(dataset_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Date", "INR_Rate"])
                writer.writerows(data)

            self.set_dataset_path(self.dataset_path)

            return {
                "success": True,
                "message": f"Успешно сохранено {len(data)} записей в dataset.csv",
                "records_count": len(data),
            }
        except Exception as e:
            return {"error": f"Ошибка загрузки данных: {e}"}

    def _get_inr_rate(self, date_str):
        """Получить курс INR с ЦБ РФ и привести к стандарту 1 INR = X RUB"""
        url = f"https://www.cbr-xml-daily.ru/archive/{date_str}/daily_json.js"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                nominal = data["Valute"]["INR"][
                    "Nominal"
                ]  # получаем номинал (1, 10, 100)
                value = data["Valute"]["INR"]["Value"]  # получаем значение
                # Приводим к стоимости 1 INR
                rate_per_one = value / nominal
                return rate_per_one
            else:
                return None
        except Exception:
            return None

    def _generate_date_range(self, start_date, end_date):
        """Сгенерировать диапазон дат"""
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date.strftime("%Y/%m/%d"))
            current_date += timedelta(days=1)
        return dates


# Создаем глобальный экземпляр процессора
data_processor = DataProcessor()
