FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r ./nosql_flask_app_requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8011

# Run app.py when the container launches

CMD ["python", "nosql_flask_app.py"]

