#Perform transcription on given audio file using the authentication keys in the given JSON file. THIS FUNCTION IS FOR USE WITH PYTHON ONLY. MATLAB FUNCTION IS BELOW.
#Required variables:
#bucket_path : String. Path to the file in the bucket that you want transcribed.
#GOOGLE_AUTH_JSON_PATH : String. Path to the local JSON file containing the authenitcation credentials for Google Cloud
def transcribe_gcs(bucket_path, GOOGLE_AUTH_JSON_PATH):
    from google.cloud import speech
    import os
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_AUTH_JSON_PATH
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=bucket_path)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
        enable_word_time_offsets=True,
        enable_automatic_punctuation=True,
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    print("Waiting for operation to complete...")
    response = operation.result(timeout=90)

    for result in response.results:
        print(u"Transcript: {}".format(result.alternatives[0].transcript))
        print("Confidence: {}".format(result.alternatives[0].confidence))

    result = response.results[-1]
    words_info = result.alternatives[0].words
    words_list = list(words_info)
    words_str_list = []
    #words_str = words_str.split(",")

    for i in range(len(words_list)):
        words_str_list.append(str(words_list[i]))
    words_str_list = [n.replace("\n", "") for n in words_str_list]
    #print(words_str_list)
    final_words = ""
    for l in words_str_list:
        final_words += (l + "\n")
    print(final_words)


    return response, words_str_list

#Perform transcription on given audio file using the authentication keys in the given JSON file. Uses diarization to attempt to differentiate multiple speakers.
#Required variables:
#bucket_path : String. Path to the file in the bucket that you want transcribed.
#GOOGLE_AUTH_JSON_PATH : String. Path to the local JSON file containing the authenitcation credentials for Google Cloud.
#num_speakers : String or Int. The number of speakers that diarization should expect. Should be passed as a whole number integer in either string or int format.
#save_cloud: Boolean. Indicates whether to save the transcription output to Google Cloud.
def transcribe_gcs_multi(bucket_path, GOOGLE_AUTH_JSON_PATH, num_speakers, save_cloud):
    #Import things. I imported re on the hope that it would encourage me to learn regex. This did not happen.
    from google.cloud import speech_v1p1beta1 as speech
    import os
    import re
    
    #Set important variables.
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_AUTH_JSON_PATH
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=bucket_path)
    num_speakers = int(num_speakers)
    dirname = os.path.dirname(os.path.abspath(__file__))
    FILE_PATH_SAVE_TXT = os.path.join(dirname, 'data/temp.txt')

    #Make speech recognition configuration for transcription.
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
        enable_word_time_offsets=True,
        enable_speaker_diarization=True,
        diarization_speaker_count=num_speakers,
        enable_automatic_punctuation=True,
        model='video'
    )

    #Creates a path for the transcribed file to be exported to the bucket. FEATURE NOT IMPLEMENTED YET. (But maybe someday.)
    output_path = bucket_path[:-4] + "_TRANSCRIPT.txt"
    output_config_x = speech.TranscriptOutputConfig(
        gcs_uri=output_path
    )
    print(output_path)

    #Performs the transcription.
    operation = client.long_running_recognize(config=config, audio=audio)
    print("Waiting for operation to complete...")
    response = operation.result(timeout=1800)

    #Prints results.
    for result in response.results:
        print(u"Transcript: {}".format(result.alternatives[0].transcript))
        print("Confidence: {}".format(result.alternatives[0].confidence))

    #Prepares things to pass to the translate_output function for translation into a list of lists.
    result = response.results[-1]
    words_info = result.alternatives[0].words
    words_list = list(words_info)
    words_str_list = []
    #words_str = words_str.split(",")
    for i in range(len(words_list)):
        words_str_list.append(str(words_list[i]))
    words_str_list = [n.replace("\n", "") for n in words_str_list]
    lofl_less = translate_output(words_str_list)

    #If the user chose to save the transcription output to the google cloud bucket, this takes the transcription and writes it to a temporary text file that is then uploaded to the bucket and then deleted.
    bucket_list = bucket_path.split("/")
    #print(bucket_list)
    bucket_name = bucket_list[2]
    destination_blob_name = "TranscriptionOutput/" + bucket_list[-1][:-4] + "_OUTPUT"
    #print(bucket_name, destination_blob_name)

    if save_cloud:
        with open(FILE_PATH_SAVE_TXT, 'w') as writer:
            for thing in range(len(lofl_less)):
                for line in lofl_less[thing]:
                    writer.write(line + " ")
                writer.write("\n")
        upload_blob(bucket_name, FILE_PATH_SAVE_TXT, destination_blob_name, GOOGLE_AUTH_JSON_PATH)
        os.remove(FILE_PATH_SAVE_TXT)

    #Return the relevant values.
    return response, words_str_list, lofl_less

#Upload a given file to the specified Google Cloud bucket so it can be accessed by longrunningrecognizer.
#Required variables:
#bucket_name : String. Name of the bucket to upload to. Google Cloud bucket names are unique identifiers. Name should be JUST the name. Not gs://whatever-the-name-is. Just whatever-the-name-is.
#source_file_name : String. Path to the file that you want uploaded to the bucket. Should be full path including drive letter just to be safe. (e.g. "C:/Users/Your-Username/Your-path-to-file/your-file.filextension")
#destination_blob_name : String. Name of the file (or blob as Google likes to call it) once uploaded to the bucket. This can be different from the original file name or the same as the original file name. Including file extensions in the name is optional.
#GOOGLE_AUTH_JSON_PATH : String. Path to the local JSON file containing the authenitcation credentials for Google Cloud.
def upload_blob(bucket_name, source_file_name, destination_blob_name, GOOGLE_AUTH_JSON_PATH):
    from google.cloud import storage
    import os
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_AUTH_JSON_PATH
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_filename(source_file_name)

    path_to_bucket_file = "gs://" + bucket_name + "/" + destination_blob_name

    print("File {} uploaded as {}".format( source_file_name, destination_blob_name))
    print("Path to new bucket file: {}".format(path_to_bucket_file))

#Delete a given file from the specified Google Cloud bucket.
#Required variables:
#bucket_name : String. Name of the bucket to upload to. Google Cloud bucket names are unique identifiers. Name should be JUST the name. Not gs://whatever-the-name-is. Just whatever-the-name-is.
#blob_name : String. Name of the file (or blob as Google likes to call it) that you wish to delete from the bucket. Assuming you uploaded directly to bucket and not to a subfolder, you can pass just the name of the blob without any path.
#GOOGLE_AUTH_JSON_PATH : String. Path to the local JSON file containing the authenitcation credentials for Google Cloud.
def delete_blob(bucket_name, blob_name, GOOGLE_AUTH_JSON_PATH):
    from google.cloud import storage
    import os
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_AUTH_JSON_PATH
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()
    print("File {} deleted from bucket {}.".format(blob_name, bucket_name))

#Translates the mess of values in Google's output to a list of lists for matlab to make sense of.
#This solution is messy as hell and likely to break at some point in the future. Good luck.
#If some wonderful person who understands regex wants to make this loads better and less complicated, feel free.
#Required variables:
#words_str_list : List. List of words as strings created in the transcribe_gcs_multi function.
def translate_output(words_str_list):
    lofl = []
    for n in words_str_list:
        for k in range(len(n)):
            if n[k] == "{":
                lofl.append(['Start Time'])
                for m in range(len(n)):
                    if n[m] == "}":
                        lofl[(words_str_list.index(n))].append(n[k:m+1])
            elif n[k:k+5] == "word:":
                lofl[(words_str_list.index(n))].append("Word: ")
                for m in range(len(n)):
                    if n[m:m+11] == 'speaker_tag':
                        lofl[(words_str_list.index(n))
                             ][5] += "{}".format(n[k+7:m-1])
                        lofl[(words_str_list.index(n))].append("Speaker: ")
                        lofl[(words_str_list.index(n))
                             ][6] += "{}".format(n[m+12:])
    lofl_less = []
    for d in range(len(lofl)):
        if '' in lofl[d]:
            lofl[d].remove('')
            lofl[d].pop(1)
            lofl[d].pop(2)
    del lofl[len(words_str_list):]
    for w in range(len(lofl)):
        for q in range(len(lofl[w])):
            lofl[w][q] = lofl[w][q].strip().replace(
                "{", "").replace("}", "|").replace(" ", "")
            if lofl[w][q][-1] == "|":
                lofl[w][q] = lofl[w][q][:-1]
        lofl[w] = [lofl[w][x].split("|") for x in range(len(lofl[w]))]
        lofl[w][0][0] += ": {}".format(lofl[w][1][0])
        lofl[w][1].pop(0)
        lofl_less.append([])
        for z in range(len(lofl[w])):
            lofl_less[w].append(lofl[w][z][0])
    seconds_yn = False
    other_seconds_yn = False
    for b in range(len(lofl_less)):
        for character in range(len(lofl_less[b][0])):
            if lofl_less[b][0][character:character+8] == "seconds:":
                seconds_yn = True
                for end_character in range(len(lofl_less[b][0])):
                    if lofl_less[b][0][end_character:end_character+6] == "nanos:":
                        lofl_less[b][0] = lofl_less[b][0].replace(
                            "seconds:", "").replace("nanos:", ".")
                    else:
                        lofl_less[b][0] = lofl_less[b][0].replace(
                            "seconds:", "")
            if not seconds_yn:
                lofl_less[b][0] = lofl_less[b][0].replace("nanos:", ".")

        for other_character in range(len(lofl_less[b][1])):
            if lofl_less[b][1][other_character:other_character+16] == "end_timeseconds:":
                other_seconds_yn = True
                for other_end_character in range(len(lofl_less[b][1])):
                    if lofl_less[b][1][other_end_character:other_end_character+6] == "nanos:":
                        lofl_less[b][1] = lofl_less[b][1].replace(
                            "end_timeseconds:", "EndTime: ").replace("nanos:", ".")
                    else:
                        lofl_less[b][1] = lofl_less[b][1].replace(
                            "end_timeseconds:", "EndTime: ")
            if not other_seconds_yn:
                lofl_less[b][1] = lofl_less[b][1].replace(
                    "end_timenanos:", "EndTime: .")

    return lofl_less

#Use to test functions and changes. Be careful when enabling this. If you leave it enabled and try to run the MATLAB script, it will call this line before running MATLAB's commands. This can greatly increase the amount of time it takes to run and can muck up the output.
#transcribe_gcs_multi('path_here', 'path_here', '2', True)
