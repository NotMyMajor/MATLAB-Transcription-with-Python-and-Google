# MATLAB-Audio-Labeler-Google-Cloud-Speech-to-Text-LongRunningRecognize-with-Python
My attempt at fixing the MATLAB Audio Labeler app's Speech-to-Text function's issues with regards to using Google's cloud-based speech-to-text service. This program leverages Python to automatically upload and run long_running_recognize on compatible audio files. No more error messages from Audio Labeler's built-in Speech-to-Text function that your audio recording is too long.

Originally intended to trancribe files for grading of speech accuracy.
Includes labels for speakers and accuracy (can be ignored if not wanted).

### This program may require an understanding of Python. It certainly wouldn't hurt.

## How It Works
1. MATLAB and its easy uigetfile function are used to allow the user to select their audio file.
2. The file is remixed to a mono .wav file if it's not already.
3. The file and necessary inforation are then passed to the Python script that uploads the file to a Google Cloud Storage bucket, performs the transcription, and passes back the results.
4. MATLAB then turns the results into a table of words with start and end times, and then further into a Labeled Signal Set (lss) linked to the audio file.
5. MATLAB then saves both the table and the lss before opening Audio Labeler and prompting the user to load the Labeled Signal Set either from the saved file or from the workspace.
