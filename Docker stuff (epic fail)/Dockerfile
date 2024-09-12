# Use the official Python image from the Docker Hub
FROM python:3.8-slim


# Set the working directory in the container
WORKDIR /app


# Copy the requirements file into the container
COPY requirements.txt .


# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Copy the rest of the application into the container
COPY . .


# Expose the port that the app will run on
EXPOSE 8000


# Command to run the application
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]





