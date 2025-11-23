import unittest
import pandas as pd
from datetime import datetime
import os
import sys

# Добавляем путь к корневой папке проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processor import DataProcessor


class TestDataProcessor(unittest.TestCase):
    """Тесты для класса DataProcessor"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.processor = DataProcessor()

        # Создаем тестовые данные
        self.test_data = pd.DataFrame(
            {
                "Date": ["2020-01-01", "2020-01-02", "2020-01-03"],
                "INR_Rate": [0.85, 0.86, 0.87],
            }
        )

        # Создаем временную папку для тестов
        self.test_dir = "test_data_dir"
        os.makedirs(self.test_dir, exist_ok=True)

        # Сохраняем тестовые данные в CSV
        self.test_csv_path = os.path.join(self.test_dir, "dataset.csv")
        self.test_data.to_csv(self.test_csv_path, index=False)

    def tearDown(self):
        """Очистка после каждого теста"""
        # Удаляем временные файлы
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_set_dataset_path_success(self):
        """Позитивный тест: успешная загрузка данных"""
        result = self.processor.set_dataset_path(self.test_dir)
        self.assertTrue(result)
        self.assertIsNotNone(self.processor.current_dataset)
        self.assertEqual(len(self.processor.current_dataset), 3)

    def test_set_dataset_path_invalid_path(self):
        """Негативный тест: неверный путь"""
        result = self.processor.set_dataset_path("/invalid/path/that/does/not/exist")
        self.assertFalse(result)

    def test_get_data_by_date_existing(self):
        """Позитивный тест: поиск по существующей дате"""
        self.processor.set_dataset_path(self.test_dir)
        result = self.processor.get_data_by_date(datetime(2020, 1, 1))
        self.assertEqual(result, 0.85)

    def test_get_data_by_date_nonexistent(self):
        """Негативный тест: поиск по несуществующей дате"""
        self.processor.set_dataset_path(self.test_dir)
        result = self.processor.get_data_by_date(datetime(2025, 1, 1))
        self.assertIsNone(result)

    def test_split_to_xy_success(self):
        """Тест разделения на X/Y файлы"""
        self.processor.set_dataset_path(self.test_dir)
        result = self.processor.split_to_xy(self.test_dir)

        self.assertTrue(result["success"])
        self.assertIn("X.csv", result["files"])
        self.assertIn("Y.csv", result["files"])

        # Проверяем что файлы созданы
        x_path = os.path.join(self.test_dir, "X.csv")
        y_path = os.path.join(self.test_dir, "Y.csv")
        self.assertTrue(os.path.exists(x_path))
        self.assertTrue(os.path.exists(y_path))


if __name__ == "__main__":
    unittest.main()
