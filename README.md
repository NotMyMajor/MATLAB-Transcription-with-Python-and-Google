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

## Setup
Before you use this program, there are a number of steps required to get everything up and working.
1. Download and extract the repository.
2. If you want more organized documentation of the MATLAB script, unzip the html folder and view the .html document.
3. Install [Python](https://www.python.org/downloads/).
4. Run the MATLAB_Speech_Recog_SETUP.py file. It should be under /PythonFiles. The script should end with this message: "Looks like everything works as intended! You're ready to begin!". If so, you can skip the next step. If not, try the next step before going further.
5. Double check that you have successfully installed the google-cloud-speech and google-cloud-storage libraries by opening a terminal, typing "python" and hitting enter to start the Python shell, and then typing "from google.cloud import speech" and pressing enter and then "from google.cloud import storage" and pressing enter. If this all works without error, you're good to proceed. If not, then you may have to [manually install](https://cloud.google.com/speech-to-text/docs/libraries) the google-cloud-speech and google-cloud-storage libraries.
6. Set up your [Google Cloud Speech-to-Text API](https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries).
7. Download your [Google Cloud authorization JSON file](https://cloud.google.com/speech-to-text/docs/libraries) and store it someplace safe. We recommend the /data folder in /PythonFiles.
8. Create a [Google Cloud Storage bucket](https://cloud.google.com/storage/docs/creating-buckets) to store your audio files.
9. Create a folder in your Google Cloud Storage bucket named __TranscriptionOutput__.
10. Change the paths for your download of the Python script folder. (Lines 49 and 50 in the GoogleSpeech2TextPipeline.m file. See image below for highlighted lines.)
11. Change the path to your Google Cloud authorization JSON file. (Line 60 in the GoogleSpeech2TextPipeline.m file.  See image below for highlighted lines.)
12. Change the name of the bucket to the name of your Google Cloud Storage bucket. (Line 56 in the GoogleSpeech2TextPipeline.m file.  See image below for highlighted lines.) *Bucket names are unique identifiers, so make sure to use **just** the name of the bucket. **NOT** gs://your_bucket_name. **JUST** your_bucket_name.*



Once all of that is complete, you should be ready to fire up MATLAB and run GoogleSpeech2TextPipeline.m. If you've set up everything correctly, it should work!

## See the html page in the html.zip folder for a gif example of loading and interacting with Audio Labeler.

## This program relies on the use of the Google Cloud Speech-to-Text API. Which is (sadly) not free. It also requires the Signal Processing and Communications toolbox for MATLAB. Ditto on the not free-ness.

I'm far from a professional programmer, so forgive me if this program has its bugs or issues.

## If you use my code to do something fun or cool, share it with me! Also, credit is nice to have too.
### Enjoy!
