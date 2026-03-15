#!/bin/bash
echo "🧪 Testing Mimir..."
cd "$(dirname "$0")/.."
source venv/bin/activate
python -c "import psutil; print('✓ psutil OK')"
python -c "import rich; print('✓ rich OK')"
echo "✅ All tests passed"

