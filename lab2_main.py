import glob
import os
import csv
import pandas as pd
from datetime import datetime, timedelta

import requests


def split_to_xy():

    # Загружаем данные
    df = pd.read_csv("dataset.csv")

    # Проверяем структуру данных
    print("Структура данных:")
    print(df.head())
    print(f"Всего строк: {len(df)}")

    # Разделяем на X.csv (даты) и Y.csv (данные)
    df[["Date"]].to_csv("X.csv", index=False)
    df[["INR_Rate"]].to_csv("Y.csv", index=False)

    print("✓ Созданы файлы:")
    print("  - X.csv (даты)")
    print("  - Y.csv (курсы INR)")
    print(f"✓ Каждый файл содержит {len(df)} строк")


def split_by_years():
    print("Текущая рабочая директория:", os.getcwd())
    print("Файлы в директории:", os.listdir("."))

    # Загружаем данные
    try:
        df = pd.read_csv("dataset.csv")
        print("✓ dataset.csv успешно загружен")
        print(f"Колонки: {df.columns.tolist()}")
        print(f"Первые строки:\n{df.head()}")

        # Преобразуем даты
        df["Date"] = pd.to_datetime(df["Date"])
        print(f"Диапазон дат: от {df['Date'].min()} до {df['Date'].max()}")

        print("\nРазделение по годам:")

        # Группируем по году
        for year, group in df.groupby(df["Date"].dt.year):
            if not group.empty:
                # Форматируем даты для названия файла
                start_date = group["Date"].min().strftime("%Y%m%d")
                end_date = group["Date"].max().strftime("%Y%m%d")
                filename = f"{start_date}_{end_date}.csv"

                # Сохраняем файл
                group.to_csv(filename, index=False)
                print(f"✓ Создан {filename} - {len(group)} записей")

        print("✓ Все файлы по годам созданы")

    except FileNotFoundError:
        print(" Ошибка: файл dataset.csv не найден!")
        print("Убедитесь, что файл находится в той же папке, что и скрипт")
    except Exception as e:
        print(f" Произошла ошибка: {e}")


def split_by_weeks():

    try:
        # Загружаем данные
        df = pd.read_csv("dataset.csv")
        df["Date"] = pd.to_datetime(df["Date"])

        print(" dataset.csv успешно загружен")
        print(f"Диапазон дат: от {df['Date'].min()} до {df['Date'].max()}")

        print("Разделение по неделям:")

        # Создаем идентификатор недели (год-неделя)
        df["YearWeek"] = (
            df["Date"].dt.isocalendar().year.astype(str)
            + "-"
            + df["Date"].dt.isocalendar().week.astype(str).str.zfill(2)
        )

        # Группируем по неделям
        created_files = 0
        for week, group in df.groupby("YearWeek"):
            if not group.empty:
                # Форматируем даты для названия файла
                start_date = group["Date"].min().strftime("%Y%m%d")
                end_date = group["Date"].max().strftime("%Y%m%d")
                filename = f"{start_date}_{end_date}.csv"

                # Сохраняем файл
                group[["Date", "INR_Rate"]].to_csv(filename, index=False)
                print(f"✓ {filename} - {len(group)} записей")
                created_files += 1

        print(f"✓ Создано {created_files} файлов по неделям")

    except FileNotFoundError:
        print(" Ошибка: файл dataset.csv не найден!")
    except Exception as e:
        print(f" Произошла ошибка: {e}")


class DataIterator:
    def __init__(self, filename: str = "dataset.csv"):
        try:
            # Загружаем и сортируем данные по дате
            self.df = pd.read_csv(filename)
            self.df["Date"] = pd.to_datetime(self.df["Date"])
            self.df = self.df.sort_values("Date").reset_index(drop=True)
            self.current_index = 0
            print(f"Итератор инициализирован. Всего записей: {len(self.df)}")
        except Exception as e:
            print(f"Ошибка инициализации итератора: {e}")
            self.df = pd.DataFrame()
            self.current_index = 0

    def next(self):
        """Возвращает кортеж (дата, данные) для следующей валидной даты"""
        if self.current_index >= len(self.df):
            return None

        # Получаем текущую строку
        row = self.df.iloc[self.current_index]
        date = row["Date"]
        data = row["INR_Rate"]

        # Переходим к следующей строке
        self.current_index += 1

        return (date, data)

    def reset(self):
        """Сбрасывает итератор в начальное состояние"""
        self.current_index = 0
        print("Итератор сброшен в начальное положение")

    def get_current_position(self):
        """Возвращает текущую позицию итератора"""
        return self.current_index


def demonstrate_iterator():
    """работа итератора"""

    iterator = DataIterator()

    print("\nПервые 10 записей:")
    for i in range(10):
        result = iterator.next()
        if result:
            date, rate = result
            print(f"{i+1:2d}. {date.strftime('%Y-%m-%d')} - {rate:.4f} RUB")
        else:
            print("Данные закончились")
            break

    print(f"\nТекущая позиция: {iterator.get_current_position()}")

    # Демонстрация сброса
    iterator.reset()

    print("\nПервые 3 записи после сброса:")
    for i in range(3):
        result = iterator.next()
        if result:
            date, rate = result
            print(f"{i+1:2d}. {date.strftime('%Y-%m-%d')} - {rate:.4f} RUB")


def get_data_single_file(date: datetime, filename: str = "dataset.csv"):
    try:
        df = pd.read_csv(filename)
        df["Date"] = pd.to_datetime(df["Date"])
        mask = df["Date"] == date
        result_df = df[mask]
        return result_df["INR_Rate"].iloc[0] if not result_df.empty else None
    except Exception:
        return None


def get_data_xy_files(date: datetime):
    try:
        dates_df = pd.read_csv("X.csv")
        data_df = pd.read_csv("Y.csv")
        dates_df["Date"] = pd.to_datetime(dates_df["Date"])
        mask = dates_df["Date"] == date
        if mask.any():
            idx = mask.idxmax()
            return data_df.iloc[idx]["INR_Rate"]
        return None
    except Exception:
        return None


def get_data_year_files(date: datetime):
    try:
        year = date.year
        pattern = f"{year}0101_{year}1231.csv"
        if os.path.exists(pattern):
            df = pd.read_csv(pattern)
            df["Date"] = pd.to_datetime(df["Date"])
            mask = df["Date"] == date
            result_df = df[mask]
            if not result_df.empty:
                return result_df["INR_Rate"].iloc[0]

        files = glob.glob(f"{year}*.csv")
        for file in files:
            if any(excluded in file for excluded in ["X.csv", "Y.csv", "dataset.csv"]):
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


def get_data_week_files(date: datetime):
    try:
        files = glob.glob("*_*.csv")
        for file in files:
            if file in ["X.csv", "Y.csv", "dataset.csv"]:
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


def demonstrate_all_versions():
    print("=== 4 ВЕРСИИ ПОИСКА ПО ДАТЕ ===")

    test_dates = [
        datetime(2016, 1, 15),
        datetime(2016, 1, 20),
        datetime(2016, 2, 5),
        datetime(2025, 1, 1),
    ]

    for i, test_date in enumerate(test_dates, 1):
        print(f"\nТест {i}: {test_date.strftime('%Y-%m-%d')}")
        print("-" * 30)

        result0 = get_data_single_file(test_date)
        result1 = get_data_xy_files(test_date)
        result2 = get_data_year_files(test_date)
        result3 = get_data_week_files(test_date)

        print(f"Версия 0: {result0}")
        print(f"Версия 1: {result1}")
        print(f"Версия 2: {result2}")
        print(f"Версия 3: {result3}")


def get_inr_rate(self, date_str):
    """Получить курс INR с ЦБ РФ и привести к стандарту 1 INR = X RUB"""
    url = f"https://www.cbr-xml-daily.ru/archive/{date_str}/daily_json.js"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            nominal = data["Valute"]["INR"]["Nominal"]  # получаем номинал (1, 10, 100)
            value = data["Valute"]["INR"]["Value"]  # получаем значение
            # Приводим к стоимости 1 INR
            rate_per_one = value / nominal
            return rate_per_one
        else:
            return None
    except Exception:
        return None


def generate_date_range(start_date, end_date):
    """
    Генерирует список дат от start_date до end_date.
    """
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y/%m/%d"))
        current_date += timedelta(days=1)
    return dates


def kurs():
    print("Начинаем сбор данных по курсу индийской рупии (INR)...")
    end_date = datetime.today()
    start_date = datetime(2016, 1, 1)  # ← Данные доступны с ~2016 года

    dates = generate_date_range(start_date, end_date)
    data = []

    for date_str in dates:
        rate = get_inr_rate(date_str)
        if rate is not None:
            formatted_date = date_str.replace("/", "-")
            data.append([formatted_date, rate])
            print(f" {formatted_date}: {rate} RUB")
        else:
            print(f"--- {date_str}: данные не найдены")

    with open("dataset.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Date", "INR_Rate"])  # ← Изменили заголовок
        writer.writerows(data)

    print(f"\n Успешно сохранено {len(data)} записей в dataset.csv")


def main():
    print(" ЛАБОРАТОРНАЯ РАБОТА 2 - ЗАПУСК ВСЕХ ЗАДАНИЙ")
    print("=" * 60)

    # Сначала создаем dataset.csv если его нет
    if not os.path.exists("dataset.csv"):
        print("\n0. СОЗДАНИЕ DATASET.CSV (загрузка данных)")
        print("-" * 40)
        kurs()

    # Задание 1: Разделение X/Y
    print("\n1.  РАЗДЕЛЕНИЕ НА X.CSV И Y.CSV")
    print("-" * 40)
    split_to_xy()

    # Задание 2: Разделение по годам
    print("\n2.  РАЗДЕЛЕНИЕ ПО ГОДАМ")
    print("-" * 40)
    split_by_years()

    # Задание 3: Разделение по неделям
    print("\n3.  РАЗДЕЛЕНИЕ ПО НЕДЕЛЯМ")
    print("-" * 40)
    split_by_weeks()

    # Задание 4: Демонстрация поиска по дате
    print("\n4.  ДЕМОНСТРАЦИЯ ПОИСКА ПО ДАТЕ")
    print("-" * 40)
    demonstrate_all_versions()

    # Задание 5: Итератор
    print("\n5.  ДЕМОНСТРАЦИЯ ИТЕРАТОРА")
    print("-" * 40)
    demonstrate_iterator()

    print("\n" + "=" * 60)
    print(" ВСЕ ЗАДАНИЯ ВЫПОЛНЕНЫ!")
    print("=" * 60)


if __name__ == "__main__":
    main()
