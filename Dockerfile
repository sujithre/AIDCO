# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 7860

# Define environment variables
ENV PYTHONUNBUFFERED=1

# Run the applicationdocker build -t <acr-name>.azurecr.io/ai-document-producer:latest .
CMD ["python", "app.py"]