# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container to /app
WORKDIR /app

# Set environment variables
ENV HOST=http://159.203.50.162
ENV TOKEN=e7026c64578833bfc1ba
ENV T_MAX=20
ENV T_MIN=10
ENV DATABASE_URL=157.230.69.113
ENV DATABASE_USER=user02eq2
ENV DATABASE_PASSWORD=Dw2OtjzSOKoZvrGN
ENV DATABASE_NAME=db02eq2

# Add Pipfiles
COPY Pipfile Pipfile.lock /app/

# Install pipenv and install dependencies
RUN pip install pipenv && pipenv install --deploy

# Copy the rest of your app's source code from your host to your image filesystem.
COPY . /app

# Run the command to start your application
CMD ["pipenv", "run", "python", "src/main.py"]