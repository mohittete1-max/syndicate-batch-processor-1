FROM python:3.10-slim

WORKDIR /app

# Install the math and web libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your engine code
COPY . .

# Open the port for Gradio
EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT=7860

# Start the engine
CMD ["python", "app.py"]
