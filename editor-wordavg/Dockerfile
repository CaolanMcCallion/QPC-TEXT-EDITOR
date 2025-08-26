# Use slim Python image for lightweight container
FROM python:3.9-slim
# Set working directory
WORKDIR /app
# Copy local files into container
COPY . .
# Install Flask and CORS library
RUN pip install flask flask-cors
# Run app when container starts
CMD ["python", "app.py"]
