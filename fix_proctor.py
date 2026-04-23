import os; path = 'backend/app/api/proctor.py'; content = [System.IO.File]::ReadAllText(); content = content.Replace('prefix=" \/proctor\\, ', ''); [System.IO.File]::WriteAllText(, content)
