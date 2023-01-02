env:
	@source env/bin/activate
dev:
	@python3 manage.py runserver localhost:8080
ngrok:
	@ngrok http 8000
