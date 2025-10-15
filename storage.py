import pickle
import os
import json

class Storage:
    def __init__(self, data_file="db.kdb"):
        self.data_file = data_file

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "rb") as f:
                    data = pickle.load(f)
                print(f"Loaded data ",data)
                return data
            except Exception as e:
                print("Failed to load data Exception: ",e)
        return {}

    def save_data(self,data):
        try:
            with open(self.data_file, "wb") as f:
                pickle.dump(data, f)
            print("Saved data")
        except Exception as e:
            print("Failed to save data Exception: ",e)

    def view_data(self):
        """Display stored data like MongoDB shell with colors and formatting"""
        try:
            with open(self.data_file, "rb") as f:
                data = pickle.load(f)

            if not data:
                print("📂 No data found.")
                return

            print("📂 KrishnaDB Data:\n")
            for key in sorted(data.keys()):
                value = data[key]
                # Create a JSON-like document
                doc = {"_id": key, "value": value}
                # Convert to formatted JSON string
                doc_str = json.dumps(doc, indent=4)
                # Add colors (keys = cyan, values = yellow)
                doc_str = doc_str.replace('"_id"', '\033[36m"_id"\033[0m')
                doc_str = doc_str.replace('"value"', '\033[36m"value"\033[0m')
                # Highlight string values in yellow
                doc_str = doc_str.replace(f'"{value}"', f'\033[33m"{value}"\033[0m') if isinstance(value, str) else doc_str
                print(doc_str + "\n")

        except Exception as e:
            print("Failed to load data Exception: ",e)

if __name__ == "__main__":
    storage = Storage()
    storage.view_data()
