FROM python:3.11

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app code
COPY . /app/

EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "Scripts/App_UI.py", "--server.port=8501", "--server.address=0.0.0.0"]
