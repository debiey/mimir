"""Web-based Mimir Copilot"""
from flask import Flask, render_template, request, jsonify
import subprocess
import psutil
import time
import os
import sys

# Add parent directory to path to find core modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.copilot.ai_engine import AICopilot

app = Flask(__name__)
copilot = AICopilot()

@app.route('/')
def index():
    return render_template('copilot.html')

@app.route('/api/command/suggest', methods=['POST'])
def suggest_command():
    data = request.json
    task = data.get('task', '')
    suggestion = copilot.suggest_command(task)
    return jsonify(suggestion)

@app.route('/api/command/explain', methods=['POST'])
def explain_command():
    data = request.json
    cmd = data.get('command', '')
    explanation = copilot.explain_command(cmd)
    return jsonify(explanation)

@app.route('/api/system/diagnose', methods=['GET'])
def diagnose():
    issue = request.args.get('issue', 'general')
    diagnosis = copilot.diagnose_issue(issue)
    return jsonify(diagnosis)

@app.route('/api/system/status', methods=['GET'])
def system_status():
    return jsonify({
        'cpu': psutil.cpu_percent(),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent,
        'uptime': time.time() - psutil.boot_time()
    })

@app.route('/api/command/run', methods=['POST'])
def run_command():
    data = request.json
    cmd = data.get('command', '')
    try:
        result = subprocess.run(cmd, shell=True, 
                              capture_output=True, text=True, timeout=30)
        return jsonify({
            'success': True,
            'stdout': result.stdout,
            'stderr': result.stderr
        })
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Command timed out'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

