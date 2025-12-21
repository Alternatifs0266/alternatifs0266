if [ -d ".venv" ]; then
    echo "Using existing virtual environment."
else
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi
.venv/bin/python analyze_adif.py "$@"
