FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

RUN mkdir -p /app/logs

# Copy the current directory (your repository) into the container
COPY . .

# Install Python dependencies from requirements.txt (if present)
RUN pip install --no-cache-dir --upgrade pip && \
    if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Expose the port your application will use
EXPOSE 9340

# Define the command to run your application
CMD ["python", "server.py"]