
# Face Attendance

### Introduction
This project is a face recognition-based attendance system. It includes a registration interface for capturing and registering faces and a login interface for recognizing faces and marking attendance.

### Features
Face Registration: Capture and register faces with names and IDs.
Face Recognition: Recognize registered faces and mark attendance.
Google Sheets Integration: Store attendance records in a Google Sheet.
Firebase Integration: Store face data in Firebase for easy access and synchronization.

### Anti Spoofing using Canny edge detector
[![Figure-1-Spoofing-test.jpg](https://i.postimg.cc/fTfWjCM7/Figure-1-Spoofing-test.jpg)](https://postimg.cc/TphXTrLh)
## Screenshots
#### Face Registration Interface
[![image.png](https://i.postimg.cc/DZ1CHvGY/image.png)](https://postimg.cc/bDNH2j3Q)
#### Login Interface
[![Untitled-1.jpg](https://i.postimg.cc/XqFqb0Mt/Untitled-1.jpg)](https://postimg.cc/XBj4fmYg)

## Installation
#### VERSION TESTED
* Python 3.9.21
### Required Libraries:
* pip install dlib (dlib-19.22.99-cp39-cp39-win_amd64.whl)
* pip install numpy (**used 1.26.4**)
* pip install face-recognition
* pip install opencv-python
* pip install PySide6
* pip install firebase-admin
##### RuntimeError: Unsupported image type, must be 8bit gray or RGB image.
* I **downgraded numpy** to version **1.26.4** and it worked again
* **numpy** version 2.x.x not compatible with **face-recognition**
## Setup
##### 1. Clone the repository
<pre>
<code>
git clone https://github.com/yourusername/face-attendance.git
</code>
</pre>
##### 2. Firebase Setup:
* Place your Firebase credentials file in the **firebase** folder and name it **credentials.json**.
* How to get : https://stackoverflow.com/questions/40799258/where-can-i-get-serviceaccountcredentials-json-for-firebase-admin
##### 3. Google Sheets Setup:
* Place your Google Sheets API credentials file in the root directory and name it **client_secret.json**
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
python login_pro.py
</code>