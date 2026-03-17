PYTHON ?= python3

install:
	$(PYTHON) -m pip install -r requirements.txt

preprocess:
	$(PYTHON) scripts/preprocess.py --sample-frac 0.10

train:
	$(PYTHON) scripts/train.py --sample-frac 0.10

train-safe:
	$(PYTHON) scripts/train.py --sample-frac 0.10 --safe-mode

ablation:
	$(PYTHON) scripts/run_ablation.py --sample-frac 0.05

ablation-safe:
	$(PYTHON) scripts/run_ablation.py --sample-frac 0.05 --safe-mode

api:
	PYTHONPATH=src uvicorn apps.fastapi_app:app --host 0.0.0.0 --port 8000

dashboard:
	streamlit run apps/dashboard.py

test:
	$(PYTHON) -m unittest discover -s tests

loadtest:
	$(PYTHON) scripts/load_test.py --url http://127.0.0.1:8000/predict --requests 200 --concurrency 20

demo-cases:
	$(PYTHON) scripts/find_demo_cases.py --sample-frac 0.02
