%% MATLAB Audio Labeler Google Cloud Speech-to-Text LongRunningRecognize with Python
% Uses a Python script to transcribe a .wav file and turn the transcription
% into a labeled signal set for use in AudioLabeler. 
% 
% Originally intended to trancribe files for grading of speech accuracy.
% Includes labels for speakers and accuracy (can be ignored if not wanted).
% This program may require an understanding of Python. It certainly wouldn't hurt.
%
% Python code is in the file MATLAB_Speech_Recog.py inside the /PythonFiles
% directory.

%% Before You Begin
% The following is a list of steps necessary to complete before running
% this code for the first time.

%%
% 
% # Install Python. <https://www.python.org/downloads/ Python Download Page>
% # Run the MATLAB_Speech_Recog_SETUP.py file. It should be under
% /PythonFiles. Double check that you have sucessfully installed the google-cloud-speech and google-cloud-storage libraries.
% # Set up your Google Cloud Speech-to-Text API <https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries Google Cloud Speech-to-Text API Instructions>
% # Download your Google Cloud authorization JSON file and store it
% someplace safe. We recommend the /data folder in /PythonFiles <https://cloud.google.com/speech-to-text/docs/libraries Google Cloud Speech-to-Text JSON Instructions>
% # Create a Google Cloud Storage bucket to store your audio files <https://cloud.google.com/storage/docs/creating-buckets Google Cloud Storage Bucket Instructions>
% # Create a folder in your Google Cloud Storage bucket named
% TranscriptionOutput.
% # Change the paths for your download of the Python script folder. (Lines
% 49 and 50 in the following code.)
% # Change the path to your Google Cloud authorization JSON file. (Line 60
% in the following code.)
% # Change the name of the bucket to the name of your Google Cloud Storage
% bucket. (Line 56 in the following code.) Make sure to use just the name of
% the bucket. NOT gs://your_bucket_name. Just your_bucket_name.

%% Setup and File Selection
% Does initial setup and brings up the file explorer for choosing your .wav
% file.

%%
% If you run into an error with the following code, MATLAB may be using the
% wrong version of Python. Enable the following line and add the path to
% python.exe for the correct version of Python.

% pyenv('Version', 'C:\Users\Path-To-Your-Python-Install\python.exe');

%%
% Add the correct directory to Python PATH if not already present.
P = py.sys.path;
if count(P,'C:\Users\Path-To-This-Script-Directory\PythonFiles') == 0
    insert(P,int32(0),'C:\Users\Path-To-This-Script-Directory\PythonFiles');
    disp("Added to Python PATH");
end

%%
% Set the google bucket name to send files to.
gs_bucket = "your-bucket-name-here";

%%
% Set the path to your google authorization JSON file.
google_auth_JSON_path = "C:/Users/Path-To-Your-JSON-File/Your-JSON-File.json";

%%
% Pull up file explorer and get the file name and path for the audio file to
% transcribe.
[destination_blob_name, source_file_path] = uigetfile({'*.wav;*.mp3',...
    'Audio Files (*.wav, *.mp3)';
    '*.*', 'All Files (*.*)'}, ...
    'Select Audio File');
if isequal(destination_blob_name,0)
    error("User did not select a file.");
end % For isequal
source_file_full_path = append(source_file_path, destination_blob_name);

%% Startup package check and Python PATH check.
% This check runs to make sure that the correct Python packages are
% installed and everything is on PATH nicely. If this check is being
% tripped for some reason when it shouldn't be, feel free to disable it.
ready_togo = py.MATLAB_Speech_Recog_SETUP.startup_check();
if ready_togo ~= 1
    error("Initial setup indicated that one or more Python packages are missing. Please run MATLAB_Speech_Recog_SETUP.py and follow instructions to fix.");
end % for ready_togo

%% Mono and MP3 Audio Check
% Check if audio is mono. If not, remix to mono, save the output and use
% that for the rest of the script. Also check if audio is .mp3 and, if so,
% resave as .wav and use that for the rest of the script.
f_char = filesep;
[audio_read,fs] = audioread(source_file_full_path);
[fPath, fName, fExt] = fileparts(source_file_full_path);
file_info = audioinfo(source_file_full_path);
switch lower(fExt)
    
    case '.wav'
        if size(audio_read,2) >= 2
            disp("Audio has more than one channel. Remixing to mono...");
            audio_read_mono = audio_read(:,1);
            new_mono_file = append(source_file_path, 'MONO_',destination_blob_name);
            audiowrite(new_mono_file,audio_read_mono,fs);
            source_file_full_path = append(source_file_path, 'MONO_',destination_blob_name);
        end
        
    case '.mp3'
        new_mp3_file = append(source_file_path, 'WAV_',destination_blob_name);
        new_mp3_file = replace(new_mp3_file, '.mp3', '.wav');
        audiowrite(new_mp3_file, audio_read, fs);
        source_file_full_path = new_mp3_file;
        [source_file_path, destination_blob_name] = fileparts(source_file_full_path);
        [audio_read,fs] = audioread(source_file_full_path);
        
        if size(audio_read,2) >= 2
            disp("Audio has more than one channel. Remixing to mono...");
            audio_read_mono = audio_read(:,1);
            new_mono_file = append(source_file_path, f_char, 'MONO_',destination_blob_name, '.wav');
            audiowrite(new_mono_file,audio_read_mono,fs);
            source_file_full_path = append(source_file_path, f_char, 'MONO_',destination_blob_name, '.wav');
        end
        
    otherwise
        error('Unexpected file extension: %s. Please use .wav or .mp3.', fExt);
        
end % For switch

%% MP3 to WAV Conversion
% Check if the audio file is .mp3 and convert to .wav if so.

[audio_read,fs] = audioread(source_file_full_path);

%% Upload, Transcribe, and Delete from Cloud
% Uploads the mono file to Google Cloud Storage, runs Google Cloud
% Speech-to-Text, and then deletes the mono file from Google Cloud Storage.
% _________________________________________________________________________________________________________________________________________ 

%%
% Upload the chosen file to the Google Cloud Storage bucket specified. Then
% create the path to the bucket file based on the specified bucket and
% filename. 
% 
% Even if the file already exists in the bucket, it doesn't hurt
% to use this given that the new file will simply overwrite the previous
% version.
disp("Uploading file to Google Cloud Storage bucket...");
py.MATLAB_Speech_Recog.upload_blob(gs_bucket, source_file_full_path, destination_blob_name, google_auth_JSON_path);
path_to_bucket_file = append("gs://",gs_bucket,"/",destination_blob_name);

%%
% This method performs transcription with speaker diarization enabled. The
% second to last passed term is the number of speakers to look for. 
% 
% ALWAYS MAKE SURE THIS IS A WHOLE INTEGER.
% 
% Additionally, the last term can be set to either true or false to
% indicate whether you want to save a copy of the transcription to your
% Google Cloud bucket.
disp("Running transcription on file...");
result = py.MATLAB_Speech_Recog.transcribe_gcs_multi(path_to_bucket_file, google_auth_JSON_path, "2", false);

%%
% Disabling the following will keep the uploaded file in the Google Cloud
% bucket.
disp("Deleting file from Google Cloud bucket...");
py.MATLAB_Speech_Recog.delete_blob(gs_bucket, destination_blob_name, google_auth_JSON_path);

%% Translate Results
% Translates the list of lists that Python returns into MATLAB cell arrays
% for easier use.

%%
% Grabs the correct index from the results and translates it into a cell
% array of python lists.
transcript = result{3};
list_transcript = cell(transcript);
list_transcript = list_transcript';
sz = size(list_transcript);

%%
% Creates a nX1 size cell array containing the start times.
start_time = cell(sz);
for s = 1:length(list_transcript)
    start_time{s} = string(list_transcript{s}{1});
    start_time{s} = str2double(start_time{s}{1}(11:length(start_time{s}{1})));
end

%%
% Creates a nX1 size cell array containing the end times.
end_time = cell(sz);
for e = 1:length(list_transcript)
    end_time{e} = string(list_transcript{e}{2});
    end_time{e} = str2double(end_time{e}{1}(9:length(end_time{e}{1})));
end

%%
% Creates a nX2 size cell array containing both start and end times.
ROILimits = horzcat(start_time, end_time);

%%
% Creates a nX1 cell array containing the transcribed words.
Value = cell(sz);
for w = 1:length(list_transcript)
    Value{w} = string(list_transcript{w}{3});
    Value{w} = Value{w}{1}(6:length(Value{w}{1}));
end

%%
% Creates a nx1 cell array containing the speaker numbers.
speaker = cell(sz);
for sp = 1:length(list_transcript)
    speaker{sp} = string(list_transcript{sp}{4});
    speaker{sp} = speaker{sp}{1}(9:length(speaker{sp}{1}));
end

%% Create Labeled Signal Set
% Creates the Labeled Signal Set for use in AudioLabeler. Once this set is
% created, it can be loaded from the workspace or from the saved file.
% Loading the set in AudioLabeler automatically loads the labels, timeframes, and audio
% file.

%%
% Creates a table containing the full results from transcription. You can
% save this out as a csv or something.
full_table_results = table(start_time, end_time, Value, speaker);

%%
% Convert ROILimits to a matlab matrix instead of cell array. Necessary for
% use with labeled signal set.
ROILimits=cell2mat(ROILimits);

%%
% Makes an audioDataStore object with the path to the chosen audio file.
ADS = audioDatastore(source_file_full_path);

%%
% Make the labeled signal set with the start and stop times, transcribed
% words, speaker numbers, and a blank 'correct' label for grading.
lss = labeledSignalSet(ADS);
lbldefs = signalLabelDefinition("SpeechContent", 'LabelType', 'roi', 'LabelDataType', 'string');
lbldefs_another = signalLabelDefinition("Speakers", 'LabelType', 'roi', 'LabelDataType', 'string');
lbldefs_last = signalLabelDefinition("Correct", 'LabelType', 'roi', 'LabelDataType', 'logical', 'DefaultValue', false);
addLabelDefinitions(lss, lbldefs);
addLabelDefinitions(lss, lbldefs_another);
addLabelDefinitions(lss, lbldefs_last);
resetLabelValues(lss);
setLabelValue(lss, 1, "SpeechContent", ROILimits, Value);
setLabelValue(lss, 1, "Speakers", ROILimits, speaker);
setLabelValue(lss, 1, "Correct", ROILimits);

disp("Full results written to table: full_table_results");
disp("Label set created. Named 'lss'.");

%% Saving Variables
% Saves the full results table and the labeled signal set to a .mat file for
% future use.
currentFile = mfilename( 'fullpath' );
[pathstr,~,~] = fileparts( currentFile );
save_filename = append(pathstr, "\Output\", destination_blob_name(1:(length(destination_blob_name)-4)), "-OUTPUT_ALL.mat");
save(save_filename, "full_table_results", "lss");
disp(newline);
fprintf("Full results table and labeled signal set saved to %s", save_filename);
disp(newline);

%%
% Does the same as above, but saves the variables to separate files.

% currentFile = mfilename( 'fullpath' );
% [pathstr,~,~] = fileparts( currentFile );
% save_filename_table = append(pathstr, "\Output\", destination_blob_name(1:(length(destination_blob_name)-4)), "-OUTPUT_TABLE.mat");
% save(save_filename_table, "full_table_results");
% save_filename = append(pathstr, "\Output\", destination_blob_name(1:(length(destination_blob_name)-4)), "-OUTPUT_LABELS.mat");
% save(save_filename, "lss");
% disp(newline);
% sprintf("Full results table saved to %s", save_filename_table);
% sprintf("Labeled signal set saved to %s", save_filename);
% disp(newline);

%% Opening AudioLabeler

audioLabeler;
fprintf("In audioLabeler, import label set 'lss' from workspace or from %s", save_filename);
disp(newline);

%%
% Once AudioLabeler is open, you can click Import and then choose to import
% the labeled signal set either from the workspace (where it is named 'lss')
% or from the file saved previously. 
% 
% If you chose to save both the full
% results table and the labeled signal set to the same .mat file, you can
% still import from file. AudioLabeler will simply grab the labeled signal
% set and ignore the table.

%% Example Interaction with Audio Labeler
% 
% <<OdysseyTestFixed0001-9309.gif>>
%

%% License

% MATLAB Google Speech 2 Text Pipeline and accompanying Python scripts
% for use in transcribing audio for MATLAB Audio Labeler.
% Copyright (C) 2021 Rhys Switzer
% 
% This program is free software: you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation, either version 3 of the License, or
% (at your option) any later version.
% 
% This program is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
% 
% You should have received a copy of the GNU General Public License
% along with this program.  If not, see <https://www.gnu.org/licenses/>.
