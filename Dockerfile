# Use the official Python slim image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code into the container
COPY . .

#addpostgres to sqlalchemy
RUN pip install psycopg2-binary

# Expose port 8000
EXPOSE 8000

# Run the FastAPI app with Uvicorn
CMD ["bash","-c", "alembic upgrade head && uvicorn app.main:app  --host 0.0.0.0 --port 8000"]