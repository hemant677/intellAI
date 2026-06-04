import os

def search_in_file(filepath, search_str):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if search_str in line:
            print(f"{filepath} Line {i+1}: {line.strip()}")

search_in_file('app.py', 'gemini-1.5')
search_in_file('templates/index.html', 'Gemini 1.5')
