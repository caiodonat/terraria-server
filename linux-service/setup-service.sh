#!/bin/bash
sudo cp /terraria-server/linux-service/terraria-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable terraria-server
