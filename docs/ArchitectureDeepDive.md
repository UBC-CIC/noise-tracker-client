# Architecture Deep Dive

## Architecture

![Archnitecture Diagram](./images/client_architecture.png)

## Description
### Start-Up
The application requires a configuration file to operate. A [sample configuration](../config_tmp.json) file is provided in the repository.
During the first start-up of the application, the user is prompted to enter the hydrophone operator ID. This ID is sent to the cloud and operator details are fetched from the database.
Users have the option to select the hydrophone(s) that they want to track on the system the application is installed on.
After selecting the hydrophones, the configuration file is saved in the storage and accessed when the application is restarted in the future (users are not prompted to enter their ID every time the app is opened).
When the configuration is read, the application initiates two separate threads, the analyzer thread, and the uploader thread.

### Analyzer Thread
This thread processes raw audio files and generates required metrics.
To keep track of already processed files, the application persists a list and adds each processed file name to the list. This list is stored in a text file alongside the configuration file.

The target folder (where the audio files are stored) is monitored periodically and if new files are detected, they are processed to extract the required metrics.
The results are stored in a temporary `results` folder.

### Uploader Thread
This thread checks for new results locally and uploads them to the cloud.
If the thread detects new result files, it will request an upload URL from the cloud backend, and upload the files to the hydrophone's folder in the bucket.
The local temporary results are deleted after a successful upload.
