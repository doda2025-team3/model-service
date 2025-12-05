#!/bin/bash
if [ ! -f "output/preprocessor.joblib" ]; then
    echo "Preprocessor not found - generating..."
    python src/text_preprocessing.py
fi

python src/serve_model.py
