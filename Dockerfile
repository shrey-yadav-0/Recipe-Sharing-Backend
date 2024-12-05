# Use the official Python image as a base
FROM python:3.12

# Create a non-root user
RUN useradd flask-user

# Set the working directory in the container
WORKDIR /home/recipe-sharing-backend-application

# Copy the required files and packages into the container
COPY app app
COPY requirements.txt .
COPY wsgi.py .

# Install dependencies
RUN pip install -r requirements.txt

# Change permissions for read, write and execute of current directory
RUN chmod -R 770 *

# Change the ownership of current directory
RUN chown -R flask-user:flask-user *

# Expose the port
EXPOSE 5000

# Switch to non-root user
USER flask-user

# Command to run the application
CMD ["flask", "--app", "wsgi", "run", "--host=0.0.0.0", "--port=5000"]
