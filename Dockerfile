FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose the port
EXPOSE 8000

# Use ENTRYPOINT to specify the command
ENTRYPOINT ["python", "api.py"] 