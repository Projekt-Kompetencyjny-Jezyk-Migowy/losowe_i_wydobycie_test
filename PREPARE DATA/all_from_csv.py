import os
import pandas as pd
from glob import glob

def main():
    try:
        # Folder z plikami CSV
        folder_path = "PREPARE DATA\gotowe_csv"
        print(f"🔍 Analiza folderu: '{folder_path}'")

        if not os.path.exists(folder_path):
            print(f"❌ Folder '{folder_path}' nie istnieje.")
            return

        csv_files = glob(os.path.join(folder_path, "*.csv"))

        if not csv_files:
            print(f"⚠️ Brak plików CSV w folderze '{folder_path}'.")
            return

        print(f"✅ Znaleziono {len(csv_files)} plik(ów) CSV.")

        # Lista do zbierania przetworzonych danych
        merged_data = []

        # Iteracja po plikach CSV
        for file in csv_files:
            label = os.path.splitext(os.path.basename(file))[0]  # np. "a" z "a.csv"
            print(f"📄 Przetwarzanie pliku: {file}")

            df = pd.read_csv(file)
            grouped = df.groupby("image_id")

            for image_id, group in grouped:
                sorted_group = group.sort_values(by="series_num").reset_index(drop=True)

                row_data = {
                    "label": label,
                    "image_id": image_id,
                }

                for i, (_, row) in enumerate(sorted_group.iterrows()):
                    for col in row.index:
                        if col in ["target", "image_id", "series_num"]:
                            continue
                        row_data[f"{i}_point_{col}"] = row[col]

                merged_data.append(row_data)

        # Stworzenie DataFrame ze złączonych danych
        final_df = pd.DataFrame(merged_data)

        # Save to Excela
        output_file = "złączone_dane.xlsx"
        final_df.to_excel(output_file, index=False)
        print(f"✅ Zapisano dane do pliku: {output_file}")
        print("🎉 Proces zakończony sukcesem.")

    except Exception as e:
        print(f"❌ Wystąpił błąd: {e}")
        print("⛔ Proces zakończony niepowodzeniem.")

if __name__ == "__main__":
    main()
