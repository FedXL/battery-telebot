#!/bin/bash

# Завершаем старый процесс
pkill -f "python run_bot.py"

# Запускаем новый процесс
nohup python run_bot.py > bot.log 2>&1 &
echo "Bot restarted successfully."