unit:
	py.test -v

coverage:
	py.test --cov=orchestrator --cov-report=html --cov-report=term-missing

production:
	gunicorn orchestrator:app -b 127.0.0.1:5020 --worker-class aiohttp.GunicornWebWorker

develop:
	gunicorn orchestrator:app -b 127.0.0.1:5020 --worker-class aiohttp.GunicornWebWorker --reload
