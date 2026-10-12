import sys

modules = [
    'fastapi',
    'uvicorn',
    'pydantic',
    'pydantic_settings',
    'sqlalchemy',
    'aiosqlite',
    'sklearn',
    'sentence_transformers',
    'fitz',
    'docx',
    'reportlab',
    'dotenv',
]

missing = []
for mod in modules:
    try:
        __import__(mod)
        print(f"[OK] {mod}")
    except Exception as e:
        print(f"[MISSING] {mod} -> {e}")
        missing.append(mod)

if missing:
    print(f"\nTotal missing: {len(missing)}")
    sys.exit(1)
else:
    print("\nAll backend dependencies installed!")
    sys.exit(0)
