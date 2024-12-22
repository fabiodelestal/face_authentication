# Facial Recognition Authentication and Encryption System

This Python script implements a facial recognition authentication system that allows users to protect and unlock files or folders using their face. It utilizes OpenCV for facial recognition and the `cryptography` library for encrypting and decrypting data. Users can register their faces, train a facial recognition model, and then authenticate themselves to secure or access their files.

## Features

- **Face Registration**: Register new users by capturing facial images.
- **Model Training**: Train a facial recognition model based on registered faces.
- **Facial Authentication**: Authenticate users using the webcam and facial recognition.
- **File/Folder Encryption**: Encrypt files or folders after successful authentication.
- **File/Folder Decryption**: Decrypt files or folders after successful authentication.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [1. Register a New Face](#1-register-a-new-face)
  - [2. Train Recognition Model](#2-train-recognition-model)
  - [3. Protect Files or Folders](#3-protect-files-or-folders)
  - [4. Unlock Files or Folders](#4-unlock-files-or-folders)
  - [5. Exit](#5-exit)
- [File Structure](#file-structure)
- [Important Notes](#important-notes)
- [Troubleshooting](#troubleshooting)
- [Dependencies](#dependencies)


## Requirements

- **Python 3.x**
- **Webcam**: A functional webcam connected to your computer.
- **Python Libraries**:
  - `opencv-python`
  - `opencv-contrib-python`
  - `cryptography`
  - `numpy`
  - `tkinter` (usually included with Python)
  - `pickle`

## Installation

1. **Clone the Repository or Download the Script**:

   ```bash
   git clone https://github.com/fabiodelestal/face_authentication
   ```

2. **Install Required Packages**:

   ```bash
   pip install opencv-python opencv-contrib-python cryptography numpy
   ```

   *Note*: `tkinter` is typically included with Python on Windows and macOS. If not, you may need to install it separately.

3. **Set Up Directory Structure**:

   The script automatically creates necessary directories, but ensure you have the following structure:

   ```
   datos/
     ├── caras_registradas/
     ├── claves/
     └── modelos/
   ```

## Usage

Run the script from your terminal or command prompt:

```bash
python main.py
```

### Main Menu

After running the script, you'll see the following menu:

```
--- Facial Authentication System ---
1. Register a new face
2. Train recognition model
3. Protect files or folders
4. Unlock files or folders
5. Exit
Select an option:
```

### 1. Register a New Face

- **Purpose**: Capture facial images for a new user.
- **Steps**:
  1. Select option `1`.
  2. Enter the user's name when prompted.
  3. The webcam will activate and capture 20 images of your face.
     - Ensure good lighting and position yourself in front of the camera.
     - Press `'q'` to exit early if needed.
  4. The images are saved in `datos/caras_registradas/<username>/`.

### 2. Train Recognition Model

- **Purpose**: Train the facial recognition model with the registered faces.
- **Steps**:
  1. Select option `2`.
  2. The script collects all registered faces and trains the LBPH (Local Binary Patterns Histograms) model.
  3. The model and label dictionary are saved in `datos/modelos/`.

### 3. Protect Files or Folders

- **Purpose**: Encrypt files or folders using your facial authentication.
- **Steps**:
  1. Select option `3`.
  2. The system will attempt to authenticate you via the webcam.
     - Position yourself clearly in front of the camera.
  3. Upon successful authentication, a file dialog will appear.
  4. Select the file or folder you wish to encrypt.
  5. The data will be encrypted using your unique key, and files will be overwritten with the encrypted data.

### 4. Unlock Files or Folders

- **Purpose**: Decrypt previously encrypted files or folders using your facial authentication.
- **Steps**:
  1. Select option `4`.
  2. Authenticate via the webcam as in step 3.
  3. Select the encrypted file or folder via the file dialog.
  4. The data will be decrypted using your unique key, restoring the original contents.

### 5. Exit

- Select option `5` to exit the program.

## File Structure

- **`datos/caras_registradas/`**: Contains folders for each registered user with their facial images.
- **`datos/claves/`**: Stores the encryption keys for each user (`<username>.key`).
- **`datos/modelos/`**: Contains the trained facial recognition model (`modelo_lbph.yml`) and label dictionary (`label_dict.pkl`).

## Important Notes

- **Unique Keys per User**: Each user has a unique encryption key generated during face registration, ensuring data encrypted by one user cannot be decrypted by another.
- **Encryption Method**: Uses symmetric encryption via the `Fernet` module from the `cryptography` library.
- **Facial Recognition**: Relies on OpenCV's LBPH algorithm for recognizing faces.
- **Data Overwrite**: Encrypted and decrypted files overwrite the original files. Ensure you have backups if necessary.

## Troubleshooting

- **Camera Issues**:
  - Ensure your webcam is properly connected and not being used by another application.
  - Test the webcam independently to confirm it's working.
- **Poor Recognition**:
  - Make sure your face is well-lit and clearly visible to the camera.
  - Remove any accessories like glasses or hats during authentication if they weren't present during registration.
- **Model Not Found**:
  - If you receive an error about the model not being found, ensure you've trained the model after registering faces.
- **Key Errors**:
  - If the script can't find your encryption key, ensure you've registered your face and haven't deleted the key file in `datos/claves/`.

## Dependencies

- **OpenCV**:
  - `opencv-python`: For capturing and processing images.
  - `opencv-contrib-python`: Provides the `face` module for facial recognition.
- **Cryptography**:
  - `cryptography`: For encryption and decryption of files and folders.
- **NumPy**:
  - `numpy`: Used in conjunction with OpenCV for numerical operations.
- **Tkinter**:
  - `tkinter`: For file dialog operations to select files and folders.
- **Pickle**:
  - `pickle`: For saving and loading the label dictionary.

