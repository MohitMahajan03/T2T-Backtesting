import os
import datetime

directory_path = "reports"  # Replace with your actual directory path
file_extension = ".csv"
older_than_hours = 24


def delete_old_csv_files():
    now = datetime.datetime.now()
    cutoff_time = now - datetime.timedelta(hours=older_than_hours)

    for filename in os.listdir(directory_path):
        if filename.endswith(file_extension):
            file_path = os.path.join(directory_path, filename)
            last_modified_time = datetime.datetime.fromtimestamp(
                os.path.getmtime(file_path)
            )

            if last_modified_time < cutoff_time:
                os.remove(file_path)
                print(f"Deleted {filename}")


if __name__ == "__main__":
    delete_old_csv_files()
