# RippleWriter Studio — Modular Refactor Phase 2
# ---------------------------------------------
# Logs session start and launches Streamlit refactor app

$phase = "Refactor Phase 2"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$logFile = "C:\Users\kevin\Documents\RippleWriter\ripplewriter_session_log.txt"

# Write log entry
"[$timestamp] $phase started." | Out-File -Append -FilePath $logFile

# Navigate to app folder
cd "C:\Users\kevin\Documents\RippleWriter\app"

# Activate environment
conda activate marketmind310

# Launch Streamlit app
streamlit run app_refactored.py --server.runOnSave true
