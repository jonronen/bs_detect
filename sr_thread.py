#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class
import subprocess
import os
import pyaudio
import time
import wave
from threading import Thread
from queue import Queue
import speech_recognition as sr
import bullshit_action as ba
import buzzwords

bullShitList = buzzwords.buzzword_list
BS_THRESHOLD = 10

r = sr.Recognizer()
audio_queue = Queue()

os.system("./bullshit_start.sh")

# Local func to record audio
def record_chunk(f_name):
	form_1 = pyaudio.paInt16 # 16-bit resolution
	chans = 1 # 1 channel
	samp_rate = 44100 # 44.1kHz sampling rate
	chunk = 4096 # 2^12 samples for buffer
	record_secs = 4 # seconds to record
	dev_index = 9 # device index found by p.get_device_info_by_index(ii)
	#wav_output_filename = 'test1.wav' # name of .wav file

	audio = pyaudio.PyAudio() # create pyaudio instantiation

	# create pyaudio stream
	stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
			input_device_index = dev_index,input = True, \
			frames_per_buffer=chunk)
	print("recording")
	frames = []

	# loop through stream and append audio chunks to frame array
	for ii in range(0,int((samp_rate/chunk)*record_secs)):
		data = stream.read(chunk)
		frames.append(data)

	print("finished recording")

	# stop the stream, close it, and terminate the pyaudio instantiation
	stream.stop_stream()
	stream.close()
	audio.terminate()

	# save the audio frames as .wav file
	wavefile = wave.open(f_name,'wb')
	wavefile.setnchannels(chans)
	wavefile.setsampwidth(audio.get_sample_size(form_1))
	wavefile.setframerate(samp_rate)
	wavefile.writeframes(b''.join(frames))
	wavefile.close()

def recognize_worker():
	bsScore = 0
	# this runs in a background thread
	while True:
		f_name = audio_queue.get()  # retrieve the next audio processing job from the main thread
		print("f_name: {}".format(f_name))
		if f_name is None: break  # stop processing if the main thread is done

		# received audio data, now we'll recognize it using Google Speech Recognition
		try:
			# for testing purposes, we're just using the default API key
			# to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
			# instead of `r.recognize_google(audio)`
			sound = sr.AudioFile(f_name)
			with sound as source:
				audio = r.record(source)
				data = r.recognize_google(audio)
				print("\n \n You SAID: " + data)

				wordList = data.split(' ')
				print("\n \n Word List: " + str(wordList))

				# Compare words
				for wrd in wordList:
					if wrd in str(bullShitList):
						bsScore = bsScore + 1
						print("BULLSHIT word!!!")

				if bsScore > BS_THRESHOLD:
					ba.take_action("up")
					bsScore = 0
					time.sleep(10)


		except sr.UnknownValueError:
			print("Google Speech Recognition could not understand audio")
		except sr.RequestError as e:
			print("Could not request results from Google Speech Recognition service; {0}".format(e))

		print("Deleting file: {}".format(f_name))
		os.system("rm {}".format(f_name))

	audio_queue.task_done()  # mark the audio processing job as completed in the queue


# start a new thread to recognize audio, while this thread focuses on listening
recognize_thread = Thread(target=recognize_worker)
recognize_thread.daemon = True
recognize_thread.start()

# Start recording main thread
try:
	i = 0
	stop = False
	while True:  # repeatedly listen for phrases and put the resulting audio on the audio processing job queue
		print("\n Say something: \n")
		cur_f_name = "test_filename_{}".format(i)
		record_chunk(cur_f_name)
		audio_queue.put(cur_f_name)	
		i = i+1

except KeyboardInterrupt:  # allow Ctrl + C to shut down the program
	print("\n Interrupted!!! \n")
	pass

audio_queue.join()  # block until all current audio processing jobs are done
audio_queue.put(None)  # tell the recognize_thread to stop
recognize_thread.join()  # wait for the recognize_thread to actually stop
