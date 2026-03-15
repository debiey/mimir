#!/bin/bash
echo "🔨 Building Mimir package..."
cd "$(dirname "$0")/.."
python setup.py sdist bdist_wheel
echo "✅ Build complete"

