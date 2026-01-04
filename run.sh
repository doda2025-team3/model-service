#!/bin/bash
set -e

OUTPUT_DIR="${OUTPUT_DIR:-/app/output}"
MODEL_DIR="${MODEL_DIR:-/models}"

PREPROCESSOR_FILE="${MODEL_DIR}/preprocessor.joblib"
MODEL_FILE="${MODEL_DIR}/model.joblib"
PREPROCESSOR_PATH="${OUTPUT_DIR}/preprocessor.joblib"
MODEL_PATH="${OUTPUT_DIR}/model.joblib"

if [ ! -f "${PREPROCESSOR_PATH}" ] || [ ! -f "${MODEL_FILE}" ]; then
    mkdir -p "${OUTPUT_DIR}"

    python src/text_preprocessing.py
    python src/text_classification.py

    mkdir -p "${MODEL_DIR}"

    mv "${PREPROCESSOR_PATH}" "${MODEL_DIR}/"
    mv "${MODEL_PATH}" "${MODEL_DIR}/"

    cp "${MODEL_DIR}/preprocessor.joblib" "${OUTPUT_DIR}/preprocessor.joblib"

fi

echo "Starting model service..."
exec python src/serve_model.py