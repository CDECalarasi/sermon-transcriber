FROM ubuntu:latest
LABEL authors="andrewmurray"


# Install required packages
RUN apt update && apt install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-setuptools \
    python3-venv \
    && apt clean

# Install ffmpeg
RUN apt install -y ffmpeg


# Create a directory where the code will live \
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Copy the code into the container
COPY . /usr/src/app

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Make port 5006 available to the world outside this container
EXPOSE 5006

# Run the Flask application (app.py)
CMD ["python3", "app.py"]

# End of Dockerfile

