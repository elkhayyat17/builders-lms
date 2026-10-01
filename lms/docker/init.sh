#!/bin/bash
set -e

if [ -f "/home/frappe/frappe-bench/sites/lms.localhost/site_config.json" ]; then
    echo "Bench already exists and is configured, starting bench..."
    cd /home/frappe/frappe-bench
    echo "lms.localhost" > sites/currentsite.txt
    ln -sfn lms.localhost sites/localhost
    [ -f "/workspace/lms/docker/apply-patches.sh" ] && bash /workspace/lms/docker/apply-patches.sh || true
    bench start
else
    echo "Creating new bench from scratch..."
    rm -rf /home/frappe/frappe-bench

    [ -s "${NVM_DIR}/nvm.sh" ] && \. "${NVM_DIR}/nvm.sh"
    nvm use 18 2>/dev/null || true
    yarn config set ignore-engines true 2>/dev/null || true

    pyenv global 3.12.14 2>/dev/null || true
    git config --global --add safe.directory '*' || true
    bench init --frappe-branch version-15 --python /home/frappe/.pyenv/versions/3.12.14/bin/python3 --skip-redis-config-generation frappe-bench

    cd frappe-bench

    # Use containers instead of localhost
    bench set-mariadb-host mariadb
    bench set-redis-cache-host redis://redis:6379
    bench set-redis-queue-host redis://redis:6379
    bench set-redis-socketio-host redis://redis:6379

    # Remove redis, watch from Procfile
    sed -i '/redis/d' ./Procfile
    sed -i '/watch/d' ./Procfile

    bench get-app --branch version-15 payments
    bench get-app --skip-assets /workspace/lms
    bench get-app --skip-assets /workspace/builders

    bench new-site lms.localhost \
        --force \
        --mariadb-root-password 123 \
        --admin-password admin \
        --no-mariadb-socket

    bench --site lms.localhost install-app payments
    bench --site lms.localhost install-app lms
    bench --site lms.localhost install-app builders
    bench --site lms.localhost set-config developer_mode 1
    bench --site lms.localhost clear-cache
    bench use lms.localhost

    # Apply patches and build frontend
    [ -s "${NVM_DIR}/nvm.sh" ] && \. "${NVM_DIR}/nvm.sh"
    bash /workspace/lms/docker/apply-patches.sh
    nvm use 22 2>/dev/null || true
    cd /home/frappe/frappe-bench/apps/lms/frontend
    yarn install
    bash /workspace/lms/docker/apply-patches.sh
    yarn build
    cd /home/frappe/frappe-bench
    bench build --app builders
    bench --site lms.localhost migrate

    echo "lms.localhost" > sites/currentsite.txt
    ln -sfn lms.localhost sites/localhost

    bench start
fi
