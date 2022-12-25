env:
	@source env/bin/activate
dev:
	@python3 manage.py runserver
ngrok:
	@ngrok http 8000
