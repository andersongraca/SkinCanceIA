#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB_NAME="${DB_NAME:-skincancer}"
DB_USER="${DB_USER:-skincancer_app}"
DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-3306}"

if ! command -v mariadb >/dev/null 2>&1 && ! command -v mysql >/dev/null 2>&1; then
  echo "MariaDB/MySQL não encontrado. Instale mariadb-server e mariadb-client antes de continuar." >&2
  exit 1
fi

if [ -f "${ROOT_DIR}/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "${ROOT_DIR}/.env"
  set +a
fi

if [ -z "${DATABASE_URL:-}" ]; then
  DB_PASS="${DB_PASS:-$(openssl rand -hex 24)}"
  sudo mariadb --protocol=socket <<SQL
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
CREATE USER IF NOT EXISTS '${DB_USER}'@'${DB_HOST}' IDENTIFIED BY '${DB_PASS}';
ALTER USER '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
ALTER USER '${DB_USER}'@'${DB_HOST}' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'localhost';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '${DB_USER}'@'${DB_HOST}';
FLUSH PRIVILEGES;
SQL

  if [ -f "${ROOT_DIR}/.env" ]; then
    cp "${ROOT_DIR}/.env" "${ROOT_DIR}/.env.backup.$(date +%Y%m%d%H%M%S)"
  fi
  cat > "${ROOT_DIR}/.env" <<EOF
PORT=3000
DATABASE_URL=mysql://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}
ML_PROJECT_ROOT=${ROOT_DIR}
ML_PYTHON_PATH=/usr/bin/python3
ML_CNN_CHECKPOINT=${ROOT_DIR}/ml_artifacts/ham10000/cnn/best.pt
ML_VIT_CHECKPOINT=${ROOT_DIR}/ml_artifacts/ham10000/vit/best.pt
ML_HYBRID_CHECKPOINT=${ROOT_DIR}/ml_artifacts/ham10000/hybrid/best.pt
ML_DOMAIN_REFERENCE=${ROOT_DIR}/ml_artifacts/ham10000/quality_reference.json
ML_ENSEMBLE_WEIGHTS_PATH=${ROOT_DIR}/ml_artifacts/ham10000/ensemble/weights.json
ML_MODEL_VERSION=ham10000-160px-cpu-epoch2
ML_INFERENCE_TIMEOUT_MS=600000
EOF
  chmod 600 "${ROOT_DIR}/.env"
else
  echo "DATABASE_URL já existe em .env; preservando a configuração atual."
fi

cd "${ROOT_DIR}"
set -a
# shellcheck disable=SC1091
. ./.env
set +a
pnpm db:push

echo "Banco local configurado e schema aplicado."
