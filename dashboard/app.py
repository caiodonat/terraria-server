from flask import Flask, request, jsonify
import subprocess
import psutil

app = Flask(__name__)


@app.route('/', methods=['GET'])
def control_index():
    return '''
    <html>
    <head>
        <title>Terraria Dashboard</title>
        <script>
            function updateStats() {
                fetch('/htop')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('cpu').innerText = data.cpu_percent !== undefined ? data.cpu_percent + '%' : 'N/A';
                        document.getElementById('mem').innerText = data.memory_percent !== undefined ? data.memory_percent + '%' : 'N/A';
                    })
                    .catch(() => {
                        document.getElementById('cpu').innerText = 'Erro';
                        document.getElementById('mem').innerText = 'Erro';
                    });
            }
            function updateLogs() {
                fetch('/logs')
                    .then(response => response.text())
                    .then(data => {
                        var logsDiv = document.getElementById('logs');
                        logsDiv.innerHTML = data;
                        logsDiv.scrollTop = logsDiv.scrollHeight;
                    })
                    .catch(() => {
                        var logsDiv = document.getElementById('logs');
                        logsDiv.innerText = 'Erro ao carregar logs.';
                        logsDiv.scrollTop = logsDiv.scrollHeight;
                    });
            }
            function controlService(action) {
                fetch('/service/terraria-server/' + action, {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        let msg = '';
                        if (data.success !== undefined) {
                            msg = data.success ? 'Ação "' + action + '" executada com sucesso.' : 'Falha ao executar ação: ' + action;
                        } else if (data.error) {
                            msg = 'Erro: ' + data.error;
                        } else {
                            msg = 'Resposta desconhecida.';
                        }
                        document.getElementById('service-status-msg').innerText = msg;
                    })
                    .catch(() => {
                        document.getElementById('service-status-msg').innerText = 'Erro ao comunicar com o serviço.';
                    });
            }

            function updateServiceStatus() {
                fetch('/service/terraria-server/status', {method: 'GET'})
                    .then(response => response.json())
                    .then(data => {
                        var statusCircle = document.getElementById('service-status-circle');
                        var statusText = document.getElementById('service-status-text');
                        if (data.success === true) {
                            statusCircle.style.background = '#2ecc40'; // verde
                            statusText.innerText = 'Ativo';
                        } else if (data.success === false) {
                            statusCircle.style.background = '#ff4136'; // vermelho
                            statusText.innerText = 'Parado';
                        } else {
                            statusCircle.style.background = '#aaaaaa'; // cinza
                            statusText.innerText = 'Desconhecido';
                        }
                    })
                    .catch(() => {
                        var statusCircle = document.getElementById('service-status-circle');
                        var statusText = document.getElementById('service-status-text');
                        statusCircle.style.background = '#aaaaaa';
                        statusText.innerText = 'Erro';
                    });
            }
            setInterval(updateStats, 2000);
            setInterval(updateLogs, 5000);
            setInterval(updateServiceStatus, 5000);
            window.onload = function() {
                updateStats();
                updateLogs();
                updateServiceStatus();
            };
        </script>
    </head>
    <body>
        <h1>Terraria Dashboard</h1>
        <div>
            <strong>CPU:</strong> <span id="cpu">...</span><br>
            <strong>Memória:</strong> <span id="mem">...</span>
        </div>
        <hr>
        <h2>Controle do Serviço</h2>
        <div>
            <button onclick="controlService('start')">Iniciar</button>
            <button onclick="controlService('stop')">Parar</button>
            <button onclick="controlService('restart')">Reiniciar</button>
            <span style="margin-left:30px;vertical-align:middle;position:relative;">
                <span id="service-status-circle" style="display:inline-block;width:18px;height:18px;border-radius:50%;background:#aaaaaa;border:2px solid #333;vertical-align:middle;cursor:pointer;"
                    onmouseover="document.getElementById('status-legend').style.display='block'"
                    onmouseout="document.getElementById('status-legend').style.display='none'"
                ></span>
                <span id="service-status-text" style="margin-left:8px;font-weight:bold;vertical-align:middle;">...</span>
                <span id="status-legend" style="display:none;position:absolute;left:30px;top:22px;background:#fff;border:1px solid #333;padding:6px 12px;border-radius:6px;box-shadow:0 2px 8px #0002;font-size:13px;z-index:10;white-space:nowrap;">
                    <span style="color:#2ecc40;font-weight:bold;">●</span> Ativo<br>
                    <span style="color:#ff4136;font-weight:bold;">●</span> Parado<br>
                    <span style="color:#aaaaaa;font-weight:bold;">●</span> Desconhecido/Erro
                </span>
            </span>
        </div>
        <div id="service-status-msg" style="margin-top:8px;color:#007700;font-weight:bold;"></div>
        <hr>
        <h2>Logs do Servidor</h2>
        <div id="logs" style="background:#222;color:#eee;padding:10px;height:300px;overflow:auto;font-family:monospace;font-size:13px;white-space:pre-wrap;"></div>
    </body>
    </html>
    ''', 200

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open('/var/log/terraria-server.log', 'r') as f:
            logs = f.read()
        return logs.replace('\n', '<br>\n')
    except FileNotFoundError:
        return jsonify({'error': 'Log file not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/htop', methods=['GET'])
def get_htop():
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        mem_percent = mem.percent
        return jsonify({
            'cpu_percent': round(cpu_percent, 2),
            'memory_percent': round(mem_percent, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/service/terraria-server/<action>', methods=['POST', 'GET'])
def control_service(action):
    name = 'terraria-server'
    if action not in ['start', 'stop', 'restart', 'status']:
        return jsonify({'error': 'Invalid action'}), 400
    try:
        result = subprocess.run(['systemctl', action, name],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)

        return jsonify({'success': result.returncode == 0}), 201
    except Exception as e:
        return jsonify({'success': False}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
