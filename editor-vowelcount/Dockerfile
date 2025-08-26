FROM php:7.2-apache
COPY src/ /var/www/html/
# Use Python 3.9 image as the base
FROM python:3.9-slim
# Set the working directory inside the container
WORKDIR /app
# Copy all files from current directory into the container
COPY . .
# Install Flask (it's needed to run the app)
RUN pip install flask flask-cors
# Run the Python app when the container starts
CMD ["python", "app.py"]
