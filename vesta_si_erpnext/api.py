
def install_pandas():
    try:
        import pandas
        print("Pandas is already installed.")
    except ImportError:
        print("Pandas is not installed. Installing...")
        try:
            import subprocess
            subprocess.check_call(["pip", "install", "pandas"])
            print("Pandas has been successfully installed.")
        except Exception as e:
            print("Error occurred while installing Pandas:", e)