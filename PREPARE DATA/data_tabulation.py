import re
import os
import pandas as pd
from collections import defaultdict

# Litery, dla których mają zostać przetworzone foldery
static_sign = set(['a', 'b', 'c', 'e', 'i', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'w', 'y'])
move_sign = set(['a+', 'c+', 'ch', 'cz', 'd', 'e+', 'f', 'g', 'h', 'j', 'k', 'l+', 'n+', 'o+', 'rz', 's+', 'sz', 'z', 'z-', 'z+'])
base_folder = "outputdetection_data"
output_data = []

# Licznik serii dla każdego ID
series_counter = defaultdict(int)

def extract_data_from_section(section):
    lines = section.strip().split("\n")
    data = {}

    # 1) Wyciągnij target, id
    match = re.search(r"====\s*([a-zA-Z])_(\d{6})_", lines[0])
    if match:
        target, id_num = match.groups()
        data["target"] = target
        data["ID"] = id_num

        # Liczymy numer serii dla danej pary (target, ID)
        key = (target, id_num)
        series_counter[key] += 1
        data["numer_serii"] = series_counter[key]
    else:
        return None  # Jeśli nie ma dopasowania, pomijamy sekcję

    # Tymczasowe przechowanie punktów i wektorów
    points = {}
    vectors = {}

    for i in range(2, 23):
        point_match = re.match(r"\s*Punkt (\d+): x=([-\d.]+), y=([-\d.]+), z=([-\d.]+)", lines[i])
        if point_match:
            idx, x, y, z = point_match.groups()
            points[f"point_{idx}_x"] = float(x)
            points[f"point_{idx}_y"] = float(y)
            points[f"point_{idx}_z"] = float(z)

    for i in range(24, len(lines)):
        vector_match = re.match(r"\s*(\d+)→(\d+): \(([-\d.]+), ([-\d.]+), ([-\d.]+)\)", lines[i])
        if vector_match:
            from_id, to_id, x, y, z = vector_match.groups()
            key_prefix = f"vector_{from_id}-{to_id}"
            vectors[f"{key_prefix}_x"] = float(x)
            vectors[f"{key_prefix}_y"] = float(y)
            vectors[f"{key_prefix}_z"] = float(z)

    # Powiel punkty i wektory z prefixami 1_, 2_, 3_
    for i in range(1, 4):
        for k, v in points.items():
            data[f"{i}_{k}"] = v
        for k, v in vectors.items():
            data[f"{i}_{k}"] = v

    return data

# Przetwarzanie folderów
if not os.path.isdir(base_folder):
    print(f"❌ Folder główny '{base_folder}' nie istnieje.")
else:
    for folder in static_sign:
        folder_path = os.path.join(base_folder, folder)
        if not os.path.isdir(folder_path):
            print(f"⚠️ Folder '{folder}' nie istnieje — pomijam.")
            continue

        print(f"\n📁 Przetwarzanie folderu: {folder_path}")
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".txt"):
                file_path = os.path.join(folder_path, file_name)
                print(f"  🔍 Plik: {file_name}")
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    sections = content.strip().split("\n\n")
                    for section in sections:
                        extracted = extract_data_from_section(section)
                        if extracted:
                            output_data.append(extracted)
    for folder in move_sign:
        pass

# Zapis do pliku Excel
if output_data:
    df = pd.DataFrame(output_data)
    output_excel = "output.xlsx"
    df.to_excel(output_excel, index=False)
    print(f"\n✅ Dane zapisane do pliku Excel: {output_excel}")
else:
    print("\n🚫 Brak danych do zapisania.")
