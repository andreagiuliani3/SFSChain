FROM python:3.12.6-slim

# Set the working directory inside the container
WORKDIR /app

# Set terminal environment variable for color support
ENV TERM=xterm-256color

# Copy the entire project into the container's /app directory
COPY ./ /app

# Install Node.js and Python dependencies
# Install curl and gnupg (needed to add Node.js repo), build-essential (for building modules)
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    build-essential \
 && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
 && apt-get install -y nodejs \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Install Node.js packages defined in package.json
RUN npm install

# Install Python packages defined in requirements.txt without cache
RUN pip install --no-cache-dir -r requirements.txt

# Command to start the application
CMD ["python", "/app/off_chain/main.py"]
