def search_in_file(filepath, search_str):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if search_str.lower() in line.lower():
            print(f"{filepath} Line {i+1}: {line.strip()}")

search_in_file('app.py', 'indore')
