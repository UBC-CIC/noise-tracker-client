# Deployment Guide

This guide will walk you through the steps required to deploy the NoiseTracker Client application on your local machine and to distribute it to hydrophone operators.

## Prerequisites
NoiseTracker client requires that the cloud backend is deployed. Please refer to the [NoiseTracker Web Application](https://github.com/UBC-CIC/noise-tracker-web) for more information on how to deploy the backend.

## Deployment Steps
1. Clone the repository to your local machine:
    ```bash
    git clone <repo-url>
    ```
2. Inside the repository, create a virtual environment:
    ```bash
    python3 -m venv venv
    ```
3. Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
4. Install the required dependencies:
    ```bash
   pip install -r requirements.txt
   ```
5. Fill out the empty strings in `constants.py` file with the appropriate values from the cloud backend.
6. Run the client application:
    ```bash
    python3 main.py
    ```
   
## Distribution Steps
1. Create a standalone executable:
    ```bash
    pyinstaller --onefile --windowed main.py -n NoiseTracker --icon="<path-to-icon>"
    ```
2. The executable will be located in the `dist` directory. You can distribute this executable to hydrophone operators. To build for other operating systems, you need to run this process on the target operating system.


