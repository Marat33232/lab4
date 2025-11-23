import importlib
import sys


def check_module(module_name, package_name=None):
    try:
        if package_name is None:
            package_name = module_name
        module = importlib.import_module(module_name)
        if hasattr(module, "__version__"):
            print(f"{package_name}: {module.__version__}")
        else:
            print(f"{package_name}: установлен")
        return True
    except ImportError:
        print(f"{package_name}: не установлен")
        return False


def main():
    print("Проверка зависимостей...")

    dependencies = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
        ("requests", "requests"),
        ("bs4", "beautifulsoup4"),
        ("sklearn", "scikit-learn"),
        ("PySide6", "PySide6"),
        ("pytest", "pytest"),
    ]

    all_ok = True
    for module_name, package_name in dependencies:
        if not check_module(module_name, package_name):
            all_ok = False

    if all_ok:
        print("Все зависимости установлены")
    else:
        print("Некоторые зависимости отсутствуют")
        print("Запустите: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
