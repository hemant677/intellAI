with open('static/script.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_line = None
for i, line in enumerate(lines):
    if 'window.analyzeRoute =' in line:
        start_line = i + 1
        break

print(f"analyzeRoute starts at line {start_line}")
