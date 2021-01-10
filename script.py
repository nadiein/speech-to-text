import moviepy.editor as mp
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
from os import walk
import os
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt

MY_PATH = "data/"

audio = MY_PATH + "audio.wav"

r = sr.Recognizer()


def folderSize(folder):
    res = []
    for (dirpath, dirnames, filenames) in walk(folder):
        res.extend(filenames)
        break
    return res

def removeFromString(oldStr, pattern):
    newStr = re.sub(pattern, "", oldStr)
    return newStr

if "audio.wav" not in folderSize(MY_PATH):
    video = mp.VideoFileClip(r"data/video.mp4")
    video.audio.write_audiofile(r"data/audio.wav")

def getLargeAudioTranscription(path, lang):
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """
    # open the audio file using pydub
    sound = AudioSegment.from_wav(path)
    # split audio sound where silence is 700 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
        # experiment with this value for your target audio file
        min_silence_len = 500,
        # adjust this per requirement
        silence_thresh = sound.dBFS-14,
        # keep the silence for 1 second, adjustable as well
        keep_silence=500,
    )

    folder_name = MY_PATH + "audio-chunks"
    # create a directory to store the audio chunks

    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    # process each chunk 
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened, language=lang)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                text = f"{text.capitalize()}. "
                print(chunk_filename, ":", text)
                whole_text += text
    # return the text for all chunks detected
    return whole_text

def createFile(t):
    f = open(MY_PATH + "data.txt", "w+")
    
    f.write(t)

    f.close()

def readFile(f):
    d = open(f, "r+")

    return d.readlines()

arr = []

if len(folderSize(MY_PATH + "audio-chunks")) < 1:
    t = getLargeAudioTranscription(audio, "ru-RU")
    c = removeFromString(t, r"[\.]")
    createFile(c)
else:
    arr = readFile(MY_PATH + "data.txt")[0].split(" ")

dict = {i:arr.count(i) for i in arr}

sortedDict = sorted(dict.items(), key=lambda item: item[1], reverse=True)
sortedTuples = {k: v for k, v in sortedDict}

print(sortedTuples)

txt = readFile(MY_PATH + "data.txt")[0]

wordcloud = WordCloud(width=1920, height=1080, max_font_size=150, min_font_size=40).generate(txt)

plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.margins(x=0, y=0)
plt.show()

