import pytest
import pandas as pd
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from data_processor import DataProcessor
from data_analysis import DataAnalyzer


class TestIntegration:

    @pytest.fixture
    def sample_dataset_file(self, tmp_path):
        dates = pd.date_range(start="2020-01-01", end="2020-01-31", freq="D")
        rates = [1.0 + 0.01 * i for i in range(31)]

        data = {"Date": dates, "INR_Rate": rates}
        df = pd.DataFrame(data)

        dataset_path = tmp_path / "dataset.csv"
        df.to_csv(dataset_path, index=False)

        return tmp_path

    def test_full_workflow(self, sample_dataset_file):
        processor = DataProcessor()

        load_success = processor.set_dataset_path(str(sample_dataset_file))
        assert load_success == True

        date = datetime(2020, 1, 15)
        rate = processor.get_data_by_date(date)
        assert rate is not None

        analyzer = DataAnalyzer(processor)
        assert analyzer.df is not None

        missing_stats = analyzer.check_missing_values()
        assert missing_stats is not None

        analyzer.add_deviation_columns()
        assert "deviation_from_mean" in analyzer.df.columns

        filtered = analyzer.filter_by_deviation(0.05)
        assert filtered is not None

        monthly = analyzer.group_by_month()
        assert not monthly.empty

    def test_error_handling_workflow(self):
        processor = DataProcessor()

        date = datetime(2020, 1, 1)
        rate = processor.get_data_by_date(date)
        assert rate is None

        analyzer = DataAnalyzer(processor)
        assert analyzer.df is None

        missing_stats = analyzer.check_missing_values()
        assert missing_stats.empty

        analyzer.add_deviation_columns()

        stats = analyzer.calculate_statistics()
        assert stats.empty
