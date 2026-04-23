import os

files = [
    'c:/Users/0501s/OneDrive/Documents/Not_My/project 2.0/frontend/src/pages/ExamAttempt.jsx',
    'c:/Users/0501s/OneDrive/Documents/Not_My/project 2.0/frontend/src/pages/StudentDashboard.jsx'
]

replacements = {
    'ðŸ• ': '🕒',
    'ðŸ›¡ï¸ ': '🛡️',
    'ðŸ‘ ï¸ ': '👁️',
    'ðŸ“ ': '📝',
    'ðŸ  ': '🏁',
    'âŒ¨ï¸ ': '⌨️',
    'Â·': '·'
}

for filepath in files:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        for old, new in replacements.items():
            content = content.replace(old, new)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filepath}")