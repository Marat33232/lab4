import pytest
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data_analysis import DataAnalyzer
from data_processor import DataProcessor


class TestDataAnalyzer:

    @pytest.fixture
    def sample_data(self):
        dates = pd.date_range(start="2020-01-01", end="2020-01-10", freq="D")
        rates = [1.0 + 0.1 * i for i in range(10)]

        data = {"Date": dates, "INR_Rate": rates}
        return pd.DataFrame(data)

    @pytest.fixture
    def processor_with_data(self, sample_data):
        processor = DataProcessor()
        processor.current_dataset = sample_data
        return processor

    @pytest.fixture
    def analyzer(self, processor_with_data):
        return DataAnalyzer(processor_with_data)

    def test_init_success(self, processor_with_data):
        analyzer = DataAnalyzer(processor_with_data)

        assert analyzer.df is not None
        assert "inr_rate" in analyzer.df.columns
        assert "date" in analyzer.df.columns

    def test_init_no_data(self):
        processor = DataProcessor()
        analyzer = DataAnalyzer(processor)

        assert analyzer.df is None

    def test_check_missing_values_no_missing(self, analyzer):
        result = analyzer.check_missing_values()

        assert not result.empty
        assert result["missing_count"].sum() == 0

    def test_add_deviation_columns_success(self, analyzer):
        analyzer.add_deviation_columns()

        expected_columns = [
            "deviation_from_median",
            "deviation_from_mean",
            "abs_deviation_from_median",
            "abs_deviation_from_mean",
        ]

        for col in expected_columns:
            assert col in analyzer.df.columns

    def test_add_deviation_columns_no_data(self):
        processor = DataProcessor()
        analyzer = DataAnalyzer(processor)

        analyzer.add_deviation_columns()

    def test_calculate_statistics_success(self, analyzer):
        analyzer.add_deviation_columns()
        stats = analyzer.calculate_statistics()

        assert not stats.empty
        assert "mean" in stats.index
        assert "std" in stats.index

    def test_filter_by_deviation_success(self, analyzer):
        analyzer.add_deviation_columns()

        filtered = analyzer.filter_by_deviation(0.1)

        assert filtered is not None
        assert isinstance(filtered, pd.DataFrame)

    def test_filter_by_date_range_success(self, analyzer):
        start_date = "2020-01-02"
        end_date = "2020-01-05"

        filtered = analyzer.filter_by_date_range(start_date, end_date)

        assert len(filtered) == 4
        assert filtered["date"].min() >= pd.to_datetime(start_date)
        assert filtered["date"].max() <= pd.to_datetime(end_date)

    def test_filter_by_date_range_invalid_dates(self, analyzer):
        filtered = analyzer.filter_by_date_range("invalid-date", "2020-01-01")

        assert filtered.empty

    def test_group_by_month_success(self, analyzer):
        analyzer.add_deviation_columns()
        monthly_data = analyzer.group_by_month()

        assert not monthly_data.empty
        assert "year_month" in monthly_data.columns
