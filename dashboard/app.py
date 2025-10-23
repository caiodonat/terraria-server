from flask import Flask, request, jsonify, send_from_directory, Response
import subprocess
import psutil
from datetime import datetime
import re

app = Flask(__name__)
service_name = 'terraria-server'
log_file_path = '/terraria-server/server/official-server.log' # 'terraria-server/server/official-server.log'
config_path = '/terraria-server/server/serverconfig.txt'


@app.route('/', methods=['GET'])
def control_index():
    return send_from_directory('static', 'index.html')

@app.route('/logs/tail')
def tail_logs():
    try:
        with open(log_file_path, 'r') as f:
            lines = f.readlines()[-20:]
        return Response('\n'.join(line.strip() for line in lines), mimetype='text/plain')
    except Exception as e:
        return Response(f"ERROR: {str(e)}", mimetype='text/plain')

@app.route('/logs/stream')
def stream_logs():
    def event_stream():
        try:
            with open(log_file_path, 'r') as f:
                # Vai para o final do arquivo
                f.seek(0, 2)
                while True:
                    line = f.readline()
                    if line:
                        yield f"{line.strip()}\n"
                    else:
                        import time
                        time.sleep(1)
        except Exception as e:
            yield f"ERROR: {str(e)}\n"
    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/specs', methods=['GET'])
def get_specs():
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        mem_percent = psutil.virtual_memory().percent
        
        status_result = subprocess.run(
            ['systemctl', 'is-active', service_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        service_status = status_result.stdout.strip() == 'active'

        return jsonify({
            'cpu': round(cpu_percent, 2),
            'ram': round(mem_percent, 2),
            'online': service_status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/service/<action>', methods=['POST', 'GET'])
def control_service(action):
    if action not in ['start', 'stop']:
        return jsonify({'error': 'Invalid action'}), 400
    try:
        result = subprocess.run(['sudo','systemctl', action, service_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True)

        return jsonify({'success': result.returncode == 0}), 201
    except Exception as e:
        return jsonify({'success': False}), 400

@app.route('/terminal', methods=['POST'])
def control_terminal():
    data = request.get_json()
    command = data.get('command') if data else None
    try:
        result = subprocess.run(
            ['screen', '-S', service_name, '-X', 'stuff', f'{command}\r'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return jsonify({'success': result.returncode == 0}), 201
    except Exception as e:
        return jsonify({'success': False}), 400

@app.route('/world', methods=['GET'])
def download_world():
    server_world_name = 'server-world.wld'
    server_world_path= '/terraria-server/server/official-server/worlds/'
    try:
        with open(config_path, 'r') as f:
            for line in f:
                match = re.match(r'world\s*=\s*(.+)', line.strip()).group(1)
                if match:
                    server_world_path = match.rsplit('/', 1)[0]
                    server_world_name = match.split('/')[-1]
    except Exception:
        pass
    
    download_name = datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + server_world_name
    return send_from_directory(server_world_path, server_world_name, as_attachment=True, download_name=download_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
