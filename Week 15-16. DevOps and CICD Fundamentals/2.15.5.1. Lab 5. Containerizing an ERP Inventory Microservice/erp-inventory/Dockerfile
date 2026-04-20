# 1. Start with a base OS + Python environment from Docker Hub
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy our dependency list into the container
COPY requirements.txt .

# 4. Install the dependencies INSIDE the container
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of our application code
COPY app.py .

# 6. Expose the port the app runs on
EXPOSE 8080

# 7. Define the command to run when the container starts
CMD ["python", "app.py"]