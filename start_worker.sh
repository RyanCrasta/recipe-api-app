#!/bin/bash

# Create a non-root user
USERNAME=celeryuser
USERID=1000

# Check if the user already exists, if not, create it
if ! id -u $USERNAME > /dev/null 2>&1; then
    echo "Creating user $USERNAME with UID $USERID"
    adduser --disabled-password --gecos "" --uid $USERID $USERNAME
fi

# Set permissions for the working directory (optional, adjust as needed)
chown -R $USERNAME:$USERNAME /app

# Run Celery worker as the new user
su $USERNAME -c "celery -A yourapp worker --loglevel=info"
