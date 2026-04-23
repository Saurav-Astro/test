import os, glob

replacements = {
    'â€¦': '...',
    'ðŸš«': '🚫',
    'ðŸš¨': '🚨',
    'ðŸ›¡ï¸ ': '🛡️',
    'âœ…': '✅',
    'â–¶': '▶',
    'â—‹': '○',
    'â†’': '→',
    'ðŸ’»': '💻',
    'â† ': '← ',
    'âœ•': '✕',
    'âš ï¸ ': '⚠️ ',
    'ðŸ  ': '🏁',
    'â ³': '⏳',
    'â›”': '⛔',
    'ðŸ‘‹': '👋',
    'ðŸ“‹': '📋',
    'ðŸ“‚': '📁',
    'ðŸ• ': '🕒',
    'â °': '⏰',
    'ðŸ“·': '📷',
    'âŒ¨ï¸ ': '⌨️',
    'ðŸŽ¥': '🎥',
    'ðŸ‘ ï¸ ': '👁️',
    'ðŸªŸ': '🪟',
    'â ±ï¸ ': '⏱️',
    'ðŸ“ ': '📝',
    'ðŸ“Š': '📊'
}

for filepath in glob.glob('c:/Users/0501s/OneDrive/Documents/Not_My/project 2.0/frontend/src/**/*.jsx', recursive=True):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)
        
    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Fixed {filepath}')