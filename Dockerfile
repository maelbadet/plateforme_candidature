# Use the official Python runtime image
FROM python:3.13

# Install netcat for waiting on DB
RUN apt-get update && apt-get install -y netcat-openbsd

# Set the working directory
WORKDIR /app

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Make the entrypoint executable
RUN chmod +x ./entrypoint.sh

# Expose the Django port
EXPOSE 8000

# Use the entrypoint
ENTRYPOINT ["./entrypoint.sh"]
