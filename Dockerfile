
FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create folder for persistent database
RUN mkdir -p /app/data

EXPOSE 5000

CMD ["python", "app.py"]
