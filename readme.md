
# Face Attendance

### Introduction
This project is a face recognition-based attendance system. It includes a registration interface for capturing and registering faces and a login interface for recognizing faces and marking attendance.

### Features
Face Registration: Capture and register faces with names and IDs.
Face Recognition: Recognize registered faces and mark attendance.
Google Sheets Integration: Store attendance records in a Google Sheet.
Firebase Integration: Store face data in Firebase for easy access and synchronization.
## Screenshots
#### Face Registration Interface
[![image.png](https://i.postimg.cc/DZ1CHvGY/image.png)](https://postimg.cc/bDNH2j3Q)
#### Login Interface
[![image.png](https://i.postimg.cc/DZ1CHvGY/image.png)](https://postimg.cc/bDNH2j3Q)

## Installation
#### VERSION TESTED
* Python 3.9.21
### Required Libraries:
* pip install dlib (dlib-19.22.99-cp39-cp39-win_amd64.whl)
* pip install face-recognition
* pip install opencv-python
* pip install PySide6
* pip install firebase-admin
## Setup
##### 1. Clone the repository
<pre>
<code>
git clone https://github.com/yourusername/face-attendance.git
</code>
</pre>
##### 2. Firebase Setup:
* Place your Firebase credentials file in the "firebase" folder and name it "credentials.json".
* How to get : https://stackoverflow.com/questions/40799258/where-can-i-get-serviceaccountcredentials-json-for-firebase-admin
##### 3. Google Sheets Setup:
* Place your Google Sheets API credentials file in the root directory and name it client_secret.json.
* How to get: https://stackoverflow.com/questions/40136699/using-google-api-for-python-where-do-i-get-the-client-secrets-json-file-from

## Usage
### 1. Run the Registration Interface:
<pre>
<code>
python reg_new.py
</code>
</pre>
### 2. Run the Login Interface:
<pre>
<code>
python login_new.py
</code>