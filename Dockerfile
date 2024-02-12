# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container to /app
WORKDIR /app

# Add Pipfiles
COPY Pipfile Pipfile.lock /app/

# Install pipenv and install dependencies
RUN pip install pipenv && pipenv install --deploy

# Copy the rest of your app's source code from your host to your image filesystem.
COPY . /app

# Run the command to start your application
CMD ["pipenv", "run", "python", "src/main.py"]