# Use slim Python image for lightweight container
FROM python:3.9-slim
# Sets the working directory
WORKDIR /app
# Copies the local files into container
COPY . .
# Install Flask and CORS library
RUN pip install flask flask-cors
# Runs the app when container starts
CMD ["python", "app.py"]
