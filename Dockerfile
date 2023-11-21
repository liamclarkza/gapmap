FROM python:3.11-slim
WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
# Start gunicorn, adjust the number of workers as needed using -w flag
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]