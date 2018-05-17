import csv
import glob
import os

import scipy.io.wavfile as wav
import python_speech_features as pspeech
import numpy as np
import scipy.signal as sig


HOUSE = 2
YES = 1
UNK = 0

def get_max(yes_files):

    i = 0
    # 99,49
    max = 0
    os.chdir(yes_files)
    for file in glob.glob("*.wav"):
        fs, signal = wav.read(yes_files + file)
        mfcc = pspeech.mfcc(signal,fs)
        if (max < mfcc.shape[0]):
            max = mfcc.shape[0]

        i = i + 1

    return max, i


def main():

    ncep = 26

    train_files = '/home/nitin/Desktop/tensorflow_speech_dataset/train/'
    out_numpy = '/home/nitin/Desktop/tensorflow_speech_dataset/numpy/'

    test_files = '/home/nitin/Desktop/tensorflow_speech_dataset/validate/'
    test_out_numpy = '/home/nitin/Desktop/tensorflow_speech_dataset/validate/'

    predict = '/home/nitin/Desktop/tensorflow_speech_dataset/predict/'
    predict_out = '/home/nitin/Desktop/tensorflow_speech_dataset/predict/'

    xferfiles_dir = '/home/nitin/Desktop/tensorflow_speech_dataset/xferfiles_valid/'

    #create_numpy_batches(train_files,out_numpy,ncep)
    #create_numpy_batches(test_files, test_out_numpy, ncep)
    #create_numpy_batches(predict, predict_out, ncep)

    create_randomized_bottleneck_batches(xferfiles_dir)


def prepare_file_inference(file_dir,file_name):

    ncep = 26
    max = 99

    fs,signal = wav.read(file_dir + file_name)
    mfcc = pspeech.mfcc(signal=signal,samplerate=fs,numcep=ncep)
    #f, t, mfcc = sig.spectrogram(signal,fs)


    # truncate to maxlen of 99 used for training
    if(mfcc.shape[0] > 99):
        mfcc = mfcc[:99,:]

    padding = ((0, max - mfcc.shape[0]), (0, 0))
    nparr2 = np.pad(mfcc, pad_width=padding, mode='constant', constant_values=0)
    #nparr2 = np.expand_dims(nparr2,axis=0)

    return nparr2


def create_randomized_bottleneck_batches(filedir):

    #TODO: randomize

    filedirout = '/home/nitin/Desktop/tensorflow_speech_dataset/xferfiles_valid_batch/'

    inputs = []
    labels = []


    os.chdir(filedir)
    i = 1
    j = 0
    for file in glob.glob('*.npy'):

        if (file.__contains__('label')):
            file2 = file.replace('numpy_bottle_labels_','')
            nparr = np.load(file)
            labels.append(nparr.tolist())

            input_file = 'numpy_bottle_' + file2
            nparr2 = np.load(input_file)
            inputs.append(nparr2.tolist())
            i = i + 1

        if (i % 100 == 0):
            j = j + 1
            print ('creating batch:' + str(j))
            np.save(filedirout + 'bottleneck_batch_' + str(j * 100) + '.npy',np.asarray(inputs))
            np.save(filedirout + 'bottleneck_batch_label_' + str(j * 100) + '.npy',np.asarray(labels))

            inputs = []
            labels = []
            i = 1

    print ('Saving validation batch')

    np.save(filedirout + 'bottleneck_batch_valid.npy', np.asarray(inputs))
    np.save(filedirout + 'bottleneck_batch_label_valid.npy', np.asarray(labels))


def create_numpy_batches(file_dir,out_dir,ncep):

    n, count = get_max(file_dir)

    max = 99
    print (n)
    print (max)
    i = 0
    inputs = []
    labels = []
    os.chdir(file_dir)
    for file in glob.glob("*.wav"):
        print(file)
        fs,signal = wav.read(file_dir + file)
        mfcc = pspeech.mfcc(signal=signal,samplerate=fs,numcep = ncep)

        if (mfcc.shape[0] > 99):
            mfcc = mfcc[:99,:]


        padding = ((0, max - mfcc.shape[0]), (0, 0))
        nparr2 = np.pad(mfcc, pad_width=padding, mode='constant', constant_values=0)

        inputLabel = nparr2.tolist()
        inputs.append(inputLabel)

        if (file.__contains__('yes')):
            labels.append(YES)
        else:
            labels.append(UNK)

        #print (labels)

        i = i + 1


        if (i % 100 == 0 or i == count):
            npInputs = np.array(inputs)
            npLabels = np.array(labels)
            #print (npInputs.shape)
            #print (npLabels.shape)

            np.save(out_dir + 'numpy_batch' + '_' + str(i) + '.npy',npInputs)
            np.save(out_dir + 'numpy_batch_labels' + '_' + str(i) + '.npy', npLabels
                    )
            inputs = []
            labels = []

    return max, count # 99,4167


if (__name__ == '__main__'):
    main()



