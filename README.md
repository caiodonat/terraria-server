# Terraria server (self-host linux)

Self host server with dashboard management

## Getting Started

Necessário que a pasta esteja na raiz (`/`) do servidor e com todos privilegio:

```bash
cd dashboard/

python3 -m venv .venv

.venv/bin/pip install -r requirements.txt


```

```bash
sudo chmod -R 777 /terraria-server/

sudo chmod +x /terraria-server/
```

```bash
sudo chmod +x dashboard/start-app.sh
```

```bash
sudo 
```



## todo

- [ ] gerenciamento do serviço via web com senha.
- [ ] upload inicial de arquivo de mundo.
- [ ] backup/download de arquivo do mundo.
- [ ] dashboard.py configurado como serviço (systemctl).
- [ ] ...

---
