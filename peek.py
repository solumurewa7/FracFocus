with open("FracFocusCSV/FracFocusRegistry_1.csv", "r") as f:
    header = f.readline()
    first_row = f.readline()

labeld_split = header.split(",")
first_row_split = first_row.split(",")

for label, row in zip(labeld_split, first_row_split):
    print(f"{label}: {row}")