# Use the latest Ubuntu as the base image
FROM --platform=linux/amd64 ubuntu:latest

# Set non-interactive frontend for package installation to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Step 1: Prevent services from starting and install base packages
RUN echo '#!/bin/sh' > /usr/sbin/policy-rc.d && \
    echo 'exit 101' >> /usr/sbin/policy-rc.d && \
    chmod +x /usr/sbin/policy-rc.d && \
    \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    software-properties-common \
    gpg-agent \
    xfce4 \
    xfce4-goodies \
    x11vnc \
    xvfb \
    novnc \
    websockify \
    sudo \
    xfonts-base \
    dbus-x11 \
    wget \
    gnupg \
    wmctrl \
    xdotool

# Step 2: Add PPAs and install Python, Chrome, and other packages
RUN add-apt-repository -y ppa:deadsnakes/ppa && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable npm python3.11 python3.11-venv python3-pip

# Step 3: Configure Chrome wrapper and clean up
RUN echo '#!/bin/bash' > /usr/local/bin/chrome-nosandbox && \
    echo '/usr/bin/google-chrome-stable --no-sandbox "$@"' >> /usr/local/bin/chrome-nosandbox && \
    chmod +x /usr/local/bin/chrome-nosandbox && \
    update-alternatives --install /usr/bin/x-www-browser x-www-browser /usr/local/bin/chrome-nosandbox 150 && \
    update-alternatives --set x-www-browser /usr/local/bin/chrome-nosandbox && \
    # Clean up apt cache and remove temporary files
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -f /usr/sbin/policy-rc.d

# Create a non-root user 'user' with password 'ubuntu' and add to sudo group
RUN useradd -m -s /bin/bash -G sudo user && \
    echo "user:ubuntu" | chpasswd

# Copy the application source code
COPY --chown=user:user src /home/user/app

# Convert line endings for all shell scripts immediately after copying
RUN find /home/user/app -name "*.sh" -exec sed -i 's/\r$//' {} \; && \
    find /home/user/app -name "*.sh" -exec chmod +x {} \;

# Create a virtual environment
ENV VIRTUAL_ENV=/home/user/app/venv
RUN python3.11 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies
RUN pip install --no-cache-dir -r /home/user/app/requirements.txt

# Copy the entrypoint and helper scripts into the container
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# Convert ALL line endings (including entrypoint) and make executable
RUN sed -i 's/\r$//' /usr/local/bin/entrypoint.sh && \
    find /home/user/app -name "*.sh" -exec sed -i 's/\r$//' {} \; && \
    find /home/user/app -name "*.sh" -exec chmod +x {} \; && \
    chmod +x /usr/local/bin/entrypoint.sh

# Expose the noVNC port
EXPOSE 6080

# Switch to the non-root user
USER user
# Set the working directory to the user's home directory
WORKDIR /home/user

# Set the entrypoint script to run when the container starts
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Set environment variables for the user
ENV USER user
ENV HOME /home/user
