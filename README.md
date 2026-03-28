# USGA Rules of Golf Assistant

Streamlit app with three features:
- Q and A chatbot over golf rules
- Rule lookup with retrieval scoring
- Quiz mode for quick practice

## Project layout

- app.py: thin Streamlit entrypoint
- src/usga_app: application package
- data/rules_seed.json: starter dataset
- scripts/prepare_rules_dataset.py: dataset preparation helper
- requirements.txt: Python dependencies

## Local run

1. Create and activate a virtual environment.
2. Install dependencies:
   - python -m pip install -r requirements.txt
3. Ensure Ollama is running locally and at least one model is installed.
4. Optional environment configuration:
   - set OLLAMA_MODEL=gemma3:4b
   - set OLLAMA_TIMEOUT=300
   - set OLLAMA_NUM_PREDICT=160
5. Start app:
   - python -m streamlit run app.py

## Streamlit Cloud deployment notes

- The app can run in retrieval-only mode if Ollama is unavailable.
- For remote generation you must provide a reachable Ollama endpoint and model via environment variables.
- Keep large generated datasets out of git unless needed.
