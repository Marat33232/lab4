import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from typing import Optional, Tuple
import warnings

warnings.filterwarnings("ignore")


class DataAnalyzer:
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.df = None
        self._load_and_prepare_data()

    def _load_and_prepare_data(self):
        """Загрузка и подготовка данных"""
        if self.data_processor.current_dataset is not None:
            self.df = self.data_processor.current_dataset.copy()

            # Приводим названия колонок к нижнему регистру с подчеркиванием
            self.df.columns = [col.lower().replace(" ", "_") for col in self.df.columns]

            print("Структура DataFrame:")
            print(f"Колонки: {self.df.columns.tolist()}")
            print(f"Размер: {self.df.shape}")
        else:
            print("Данные не загружены в DataProcessor")

    def check_missing_values(self) -> pd.DataFrame:
        """Проверка на наличие пропущенных значений"""
        if self.df is None:
            print("Данные не загружены")
            return pd.DataFrame()

        print("=== ПРОВЕРКА ПРОПУЩЕННЫХ ЗНАЧЕНИЙ ===")

        # Статистика пропущенных значений
        missing_stats = pd.DataFrame(
            {
                "missing_count": self.df.isnull().sum(),
                "missing_percentage": self.df.isnull().mean() * 100,
            }
        )

        print(missing_stats)
        print(
            f"\nОбщее количество пропущенных значений: {self.df.isnull().sum().sum()}"
        )

        # Обработка пропущенных значений (заполнение медианой)
        if self.df["inr_rate"].isnull().any():
            median_value = self.df["inr_rate"].median()
            self.df["inr_rate"].fillna(median_value, inplace=True)
            print(
                f"Заполнено {self.df['inr_rate'].isnull().sum()} пропущенных значений медианой: {median_value:.4f}"
            )

        return missing_stats

    def add_deviation_columns(self):
        """Добавление столбцов с отклонениями от медианы и среднего"""
        if self.df is None:
            print("Данные не загружены")
            return

        print("\n=== ДОБАВЛЕНИЕ СТОЛБЦОВ С ОТКЛОНЕНИЯМИ ===")

        # Вычисляем медиану и среднее
        median_rate = self.df["inr_rate"].median()
        mean_rate = self.df["inr_rate"].mean()

        print(f"Медиана курса INR: {median_rate:.4f}")
        print(f"Среднее значение курса INR: {mean_rate:.4f}")

        # Добавляем столбцы с отклонениями
        self.df["deviation_from_median"] = self.df["inr_rate"] - median_rate
        self.df["deviation_from_mean"] = self.df["inr_rate"] - mean_rate
        self.df["abs_deviation_from_median"] = abs(self.df["deviation_from_median"])
        self.df["abs_deviation_from_mean"] = abs(self.df["deviation_from_mean"])

        print("Добавлены столбцы:")
        print("- deviation_from_median: отклонение от медианы")
        print("- deviation_from_mean: отклонение от среднего")
        print("- abs_deviation_from_median: абсолютное отклонение от медианы")
        print("- abs_deviation_from_mean: абсолютное отклонение от среднего")

        print(f"\nНовые колонки: {self.df.columns.tolist()}")

    def calculate_statistics(self) -> pd.DataFrame:
        """Вычисление статистической информации"""
        if self.df is None:
            print("Данные не загружены")
            return pd.DataFrame()

        print("\n=== СТАТИСТИЧЕСКИЙ АНАЛИЗ ===")

        # Основные статистики
        numeric_columns = [
            "inr_rate",
            "deviation_from_median",
            "deviation_from_mean",
            "abs_deviation_from_median",
            "abs_deviation_from_mean",
        ]

        stats = self.df[numeric_columns].describe()
        print("Основные статистики:")
        print(stats)

        return stats

    def filter_by_deviation(self, deviation_threshold: float) -> pd.DataFrame:
        """
        Фильтрация данных по отклонению от среднего

        Args:
            deviation_threshold: пороговое значение отклонения

        Returns:
            Отфильтрованный DataFrame
        """
        if self.df is None:
            print("Данные не загружены")
            return pd.DataFrame()

        filtered_df = self.df[
            self.df["abs_deviation_from_mean"] >= deviation_threshold
        ].copy()

        print(f"\n=== ФИЛЬТРАЦИЯ ПО ОТКЛОНЕНИЮ >= {deviation_threshold} ===")
        print(f"Найдено записей: {len(filtered_df)}")
        print(f"Процент от общего количества: {len(filtered_df)/len(self.df)*100:.2f}%")

        return filtered_df

    def filter_by_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Фильтрация данных по диапазону дат

        Args:
            start_date: начальная дата (формат: 'YYYY-MM-DD')
            end_date: конечная дата (формат: 'YYYY-MM-DD')

        Returns:
            Отфильтрованный DataFrame
        """
        if self.df is None:
            print("Данные не загружены")
            return pd.DataFrame()

        try:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)

            mask = (self.df["date"] >= start) & (self.df["date"] <= end)
            filtered_df = self.df[mask].copy()

            print(f"\n=== ФИЛЬТРАЦИЯ ПО ДАТАМ {start_date} - {end_date} ===")
            print(f"Найдено записей: {len(filtered_df)}")

            return filtered_df

        except Exception as e:
            print(f"Ошибка при фильтрации по дате: {e}")
            return pd.DataFrame()

    def group_by_month(self) -> pd.DataFrame:
        """Группировка данных по месяцам с вычислением среднего курса"""
        if self.df is None:
            print("Данные не загружены")
            return pd.DataFrame()

        print("\n=== ГРУППИРОВКА ПО МЕСЯЦАМ ===")

        # Создаем колонку с годом-месяцем
        self.df["year_month"] = self.df["date"].dt.to_period("M")

        # Группируем по месяцам
        monthly_stats = (
            self.df.groupby("year_month")
            .agg(
                {
                    "inr_rate": ["mean", "median", "std", "min", "max"],
                    "deviation_from_mean": "mean",
                    "abs_deviation_from_mean": "mean",
                }
            )
            .round(4)
        )

        # Упрощаем названия колонок
        monthly_stats.columns = [
            "_".join(col).strip() for col in monthly_stats.columns.values
        ]
        monthly_stats = monthly_stats.reset_index()
        monthly_stats["year_month"] = monthly_stats["year_month"].astype(str)

        print(f"Сгруппировано по {len(monthly_stats)} месяцам")
        print("\nСтатистика по месяцам:")
        print(monthly_stats.head(10))

        return monthly_stats

    def plot_full_period(self):
        """Построение графика курса за весь период"""
        if self.df is None:
            print("Данные не загружены")
            return

        print("\n=== ПОСТРОЕНИЕ ГРАФИКА ЗА ВЕСЬ ПЕРИОД ===")

        plt.figure(figsize=(15, 8))

        # Основной график курса
        plt.plot(
            self.df["date"],
            self.df["inr_rate"],
            linewidth=1,
            alpha=0.7,
            label="Курс INR/RUB",
        )

        # Настройки графика
        plt.title(
            "Курс индийской рупии (INR) к российскому рублю (RUB)",
            fontsize=16,
            fontweight="bold",
        )
        plt.xlabel("Дата", fontsize=12)
        plt.ylabel("Курс INR/RUB", fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend()

        # Форматирование осей
        plt.gcf().autofmt_xdate()

        plt.show()

        # Дополнительная информация
        print(
            f"Период данных: {self.df['date'].min().strftime('%Y-%m-%d')} - {self.df['date'].max().strftime('%Y-%m-%d')}"
        )
        print(f"Общее количество точек: {len(self.df)}")
        print(f"Минимальный курс: {self.df['inr_rate'].min():.4f}")
        print(f"Максимальный курс: {self.df['inr_rate'].max():.4f}")
        print(f"Средний курс: {self.df['inr_rate'].mean():.4f}")

    def plot_monthly_analysis(self, year_month: str):
        """
        Построение графика за указанный месяц с медианой и средним

        Args:
            year_month: месяц в формате 'YYYY-MM'
        """
        if self.df is None:
            print("Данные не загружены")
            return

        print(f"\n=== АНАЛИЗ ЗА МЕСЯЦ {year_month} ===")

        try:
            # Фильтруем данные за указанный месяц
            monthly_data = self.df[
                self.df["date"].dt.to_period("M") == year_month
            ].copy()

            if monthly_data.empty:
                print(f"Нет данных за месяц {year_month}")
                return

            # Вычисляем статистики
            median_value = monthly_data["inr_rate"].median()
            mean_value = monthly_data["inr_rate"].mean()

            plt.figure(figsize=(12, 6))

            # График daily курса
            plt.plot(
                monthly_data["date"],
                monthly_data["inr_rate"],
                marker="o",
                linewidth=2,
                markersize=4,
                label="Дневной курс",
            )

            # Линии медианы и среднего
            plt.axhline(
                y=median_value,
                color="red",
                linestyle="--",
                linewidth=2,
                label=f"Медиана: {median_value:.4f}",
            )
            plt.axhline(
                y=mean_value,
                color="green",
                linestyle="--",
                linewidth=2,
                label=f"Среднее: {mean_value:.4f}",
            )

            # Настройки графика
            month_name = monthly_data["date"].dt.strftime("%B %Y").iloc[0]
            plt.title(f"Курс INR/RUB за {month_name}", fontsize=14, fontweight="bold")
            plt.xlabel("Дата", fontsize=12)
            plt.ylabel("Курс INR/RUB", fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.legend()

            # Форматирование дат на оси X
            plt.gcf().autofmt_xdate()

            plt.show()

            # Вывод статистик
            print(f"Статистика за {month_name}:")
            print(f" - Количество торговых дней: {len(monthly_data)}")
            print(f" - Минимальный курс: {monthly_data['inr_rate'].min():.4f}")
            print(f" - Максимальный курс: {monthly_data['inr_rate'].max():.4f}")
            print(f" - Медиана: {median_value:.4f}")
            print(f" - Среднее: {mean_value:.4f}")
            print(f" - Стандартное отклонение: {monthly_data['inr_rate'].std():.4f}")

        except Exception as e:
            print(f"Ошибка при построении графика: {e}")
