import os
import subprocess
import re
from google import genai
from dotenv import load_dotenv

# Load environment variables from the .env file in the project root
load_dotenv()

def run_django_tests():
    """Runs the Django test suite and returns success status and output/traceback."""
    print("🚀 Running test suite: python manage.py test core...")
    result = subprocess.run(
        ["python", "manage.py", "test", "core"],
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout + "\n" + result.stderr

def gather_project_context(root_dir="."):
    """Recursively reads Python files to build holistic context for the AI."""
    codebase_context = ""
    skip_dirs = {".git", "venv", "__pycache__", "staticfiles", "media", "ai_agent"}
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for file in filenames:
            if file.endswith(".py"):
                file_path = os.path.join(dirpath, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        codebase_context += f"\n\n--- FILE: {file_path} ---\n{f.read()}"
                except Exception:
                    pass
    return codebase_context

def apply_ai_fixes(ai_response_text):
    """Parses Gemini's structured response for file blocks and writes patches to disk."""
    pattern = r"--- FILE: (.*?) ---\n```python\n(.*?)```"
    matches = re.findall(pattern, ai_response_text, re.DOTALL)
    
    if not matches:
        print("⚠️ No structured file patches found in AI response.")
        return False

    for file_path, new_code in matches:
        clean_path = file_path.strip()
        clean_path = os.path.normpath(clean_path)
        
        if os.path.exists(clean_path):
            with open(clean_path, 'w', encoding='utf-8') as f:
                f.write(new_code.strip())
            print(f"🔧 [APPLIED FIX] Successfully updated: {clean_path}")
        else:
            print(f"⚠️ Target file not found for patching: {clean_path}")
            
    return True

def autonomous_debug_loop(max_attempts=3):
    # Automatically picks up GEMINI_API_KEY from the loaded .env file
    client = genai.Client()
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n==============================================")
        print(f"🔄 Autonomous Debug Cycle {attempt} of {max_attempts}")
        print(f"==============================================")
        
        # 1. Run tests
        passed, terminal_output = run_django_tests()
        
        if passed:
            print("🎉 Success! All tests passed cleanly. No bugs detected.")
            return

        print("❌ Tests failed. Gathering holistic codebase context...")
        project_code = gather_project_context(".")
        
        # 2. Construct intelligent prompt
        prompt = f"""
        You are an autonomous Django Senior Architect and Debugging Agent.
        Your project test suite failed with the terminal output below. 
        Analyze the full project codebase and the traceback to resolve the root cause.
        
        ERROR OUTPUT / TRACEBACK:
        {terminal_output}
        
        FULL PROJECT CODEBASE:
        {project_code}
        
        CRITICAL INSTRUCTIONS:
        For every file you need to modify to fix the bug, format your response using this exact structure so the script can parse and write it automatically:
        --- FILE: path/to/file.py ---
        ```python
        # complete updated code for the file here
        ```
        """

        print("🤖 Sending code ecosystem to Gemini for deep analysis...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        # 3. Apply parsed patches
        print("📝 Applying AI-generated fixes to local project files...")
        applied = apply_ai_fixes(response.text)
        
        if not applied:
            print("🛑 Could not parse automated patches. Halting loop.")
            break

    print("\n⚠️ Max debugging attempts reached. Please review changes manually.")

if __name__ == "__main__":
    print("=== Edutrack Autonomous AI Diagnostic Agent ===")
    
    # Verify key is loaded before starting
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY not found. Please check your .env file.")
    else:
        confirm = input("This script will execute your test suite and automatically overwrite local files if errors occur. Proceed? (y/n): ")
        if confirm.lower() == 'y':
            autonomous_debug_loop()