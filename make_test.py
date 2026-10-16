import csv, sys

src = sys.argv[1] if len(sys.argv) > 1 else "urls.csv"
dst = sys.argv[2] if len(sys.argv) > 2 else "urls_test.csv"

with open(src, encoding="utf-8") as f:
    rows = list(csv.reader(f))

with open(dst, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(rows[:21])

print(dst, "written with", len(rows[:21]) - 1, "URLs from", src)