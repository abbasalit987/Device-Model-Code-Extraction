FROM python:3.9-alpine

# Install build dependencies including g++, make, and python3-dev
RUN apk update && apk add --no-cache gcc musl-dev libffi-dev g++ make python3-dev

# Set working directory
WORKDIR /app

# Copy requirements.txt to the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Command to run the app, specify correct module path
CMD ["uvicorn", "component_warranty_model.main:app", "--host", "0.0.0.0", "--port", "9500"]
