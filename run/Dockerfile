# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster


RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tk
    
# Set the working directory in the container to /app
WORKDIR /app

COPY main-noimgshow.py /app/

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements-all.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run main.py when the container launches
CMD ["python", "main.py"]