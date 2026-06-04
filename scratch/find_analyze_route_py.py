with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_line = None
for i, line in enumerate(lines):
    if 'def analyze_route():' in line:
        start_line = i + 1
        break

print(f"analyze_route starts at line {start_line}")
