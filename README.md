# DjangoAutoFix
A self-healing test automation tool for Django. It executes tests, sends failures and codebase context to Google Gemini, and writes fixes directly to disk.

# DjangoAutoFix

DjangoAutoFix is an autonomous, self-healing debugging agent designed for Django applications. Powered by Google Gemini (`gemini-2.5-flash`), it executes your test suite, detects tracebacks, gathers context across your project, and writes fixes directly to your codebase until the tests pass.

---

## How It Works

1. **Test Runner**: Automatically runs `python manage.py test core` using a subshell process.
2. **Context Harvester**: Scans your project directory recursively, ingesting relevant Python code while skipping directories like `.git`, `venv`, `staticfiles`, and media folders.
3. **AI Root-Cause Diagnosis**: Packages the terminal failure trace together with project code and prompts Gemini to produce targeted file modifications.
4. **Autonomous In-Place Patching**: Parses structured file blocks returned by the model and updates the target files on disk.
5. **Iterative Verification**: Re-runs the test suite in a self-healing loop (up to 3 cycles) to verify that the bug has been resolved.

---

## Directory Setup

Place the agent inside a dedicated folder (such as `django_autofix/`) in your Django project's root:

```text
my_django_project/
├── .env
├── manage.py
├── core/
└── django_autofix/
    ├── __init__.py
    ├── agent.py
    ├── requirements.txt
    └── README.md
