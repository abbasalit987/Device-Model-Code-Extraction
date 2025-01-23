# Component Warranty Model: Named Entity Recognition (NER) for Model Code Extraction

This repository implements a system for extracting TV and appliance model codes from textual descriptions using Named Entity Recognition (NER) powered by spaCy. It includes fine-tuned NER models for various brands, an API interface using FastAPI, and a containerized deployment setup using Docker.

---

## Project Overview

The goal of this project is to:

1. Extract model codes from textual descriptions of devices, such as:
   - **Input:** `"SAMSUNG UA43AU7700 - 43\" LED and QN90D available now."`
   - **Output:** `"UA43AU7700"`

2. Provide brand-specific fine-tuned NER models for improved accuracy.

3. Facilitate training and extraction workflows through an API built with FastAPI.

4. Enable containerized deployment using Docker and Uvicorn as the ASGI server.

---

## Key Features

1. **Fine-Tuned Brand Models:**
   - Individual spaCy models are fine-tuned for each brand (e.g., Samsung, Sony, LG) using custom training data.

2. **FastAPI Integration:**
   - API endpoints for training models and extracting model codes.

3. **Dockerized Deployment:**
   - The application is containerized for scalability and ease of deployment.

4. **Custom Tokenizer Configuration:**
   - Handles special characters in model descriptions to improve extraction accuracy.

5. **Extensible Framework:**
   - Supports addition of new brands and training data.

---

## Project Structure

```
├── component_warranty_model
│   ├── Data                # Training data grouped by brands
│   │   ├── Croma
│   │   ├── General
│   │   ├── Haier
│   │   ├── LG
│   │   ├── Panasonic
│   │   ├── Samsung
│   │   ├── Sansui
│   │   ├── Sony
│   │   ├── TCL
│   │   ├── Vise
│   │   └── Xiaomi
│   ├── spaCy              # Fine-tuned models for each brand
│   │   ├── Samsung
│   │   │   ├── fine_tune_model
│   │   │   └── __pycache__
│   │   ├── LG
│   │   │   └── fine_tune_model
│   │   └── ...
│   └── Warranty Data       # Warranty-related datasets
├── model_code_ner
│   ├── ner                 # Additional NER utilities
│   └── vocab               # Vocabulary for NER
├── Dockerfile              # Docker configuration file
├── requirements.txt        # Python dependencies
├── venv                    # Python virtual environment
└── main.py                 # FastAPI application entry point
```

---

## Dockerfile

```dockerfile
FROM python:3.9-alpine

# Install build dependencies
RUN apk update && apk add --no-cache gcc musl-dev libffi-dev g++ make python3-dev

# Set working directory
WORKDIR /app

# Copy requirements.txt to the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Command to run the app
CMD ["uvicorn", "component_warranty_model.main:app", "--host", "0.0.0.0", "--port", "9500"]
```

---

## FastAPI Endpoints

### `POST /train`
**Description:** Train or resume training of NER models for specified brands.

**Request Body:**
```json
{
  "s3_obj": {"Body": "<training_file_content>"},
  "brand": "Samsung",
  "training_type": "resume"
}
```

**Response:**
```json
{
  "message": "Training completed for the data input!"
}
```

### `GET /extract`
**Description:** Extract model codes from a given description or dataset.

**Request Body:**
```json
{
  "device_details": {"brand": "Samsung", "model": "UA43AU7700 - 43\" LED"},
  "s3_obj": {"Body": "<data_file_content>"}
}
```

**Response:**
```json
{
  "status": "success",
  "entities": ["UA43AU7700"]
}
```

### `GET /`
**Description:** Health check endpoint.

**Response:**
```json
{
  "message": "Hello! Welcome to Model Code Extraction Portal"
}
```

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Docker

### Steps

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application Locally:**
   ```bash
   uvicorn component_warranty_model.main:app --host 0.0.0.0 --port 9500
   ```

4. **Run with Docker:**
   ```bash
   docker build -t component-warranty .
   docker run -d -p 9500:9500 component-warranty
   ```

---

## Training Process

1. Upload the dataset (Excel format) containing `Brand`, `Model Description`, and `Model Code` columns to an S3 bucket.
2. Trigger the `/train` endpoint with the S3 object details.
3. The application fine-tunes the NER model for the specified brand and saves unmatched cases for review.

---

## Future Enhancements

- Add support for additional appliance categories.
- Enhance the regex logic for better model span extraction.
- Implement real-time streaming data support.

---

## Contact

For questions or suggestions, feel free to reach out via GitHub or email - abbasalit987@gmail.com

