"""
run_studio.py - Launch Retention Auto-Clipper Studio Web UI and API.
"""

import sys
import uvicorn

if __name__ == "__main__":
    print("\n==================================================================")
    print(" ⚡ RETENTION AUTO-CLIPPER STUDIO (ANTI-COPYRIGHT SHIELD ACTIVE)")
    print("==================================================================")
    print(" 🚀 Server running at: http://localhost:8000")
    print(" 📂 Open your browser and navigate to: http://localhost:8000")
    print(" 🛑 Press CTRL+C to stop the studio.")
    print("==================================================================\n")

    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=False)
