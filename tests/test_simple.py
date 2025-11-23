def test_basic():
    assert 1 + 1 == 2


def test_import():
    try:
        import data_processor
        import data_analysis

        assert True
    except ImportError as e:
        print(f"Import error: {e}")
        assert False
