# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install watchfiles for hot reload support
RUN pip install watchfiles

# Copy the rest of the application
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Define environment variable for MongoDB connection
ENV MONGO_URI="mongodb://mongo_db:27017"

# Run Uvicorn with hot reload enabled
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]