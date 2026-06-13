# 1. Define the exact OS and runtime
FROM python:3.10-slim

# 2. Set the working directory
WORKDIR /app

# 3. Install exactly the required dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the application code
COPY inventory_api.py .

# 5. Define the immutable execution command
CMD ["python", "inventory_api.py"]
