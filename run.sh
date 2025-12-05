#!/bin/bash

set -e

if [ ! -f "output/preprocessor.joblib" ]; then
    echo "Preprocessor not found - generating..."
    python src/text_preprocessing.py
fi

echo "Starting model service..."
exec python src/serve_model.py
