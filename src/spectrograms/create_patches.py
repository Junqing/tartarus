import pickle
import numpy as np
import os
import sys
sys.path.insert(0, '../')
import common
import librosa
import h5py

SECONDS = 15
SR = 22050
HR = 1024
N_FRAMES = int(SECONDS * SR / float(HR)) # 10 seconds of audio
N_SAMPLES=1
N_BINS = 96
DATASET_NAME='MSD-AG-S'
SPECTRO_DATASET='MSD'
Y_PATH='als_200'

def sample_patch(mel_spec, n_frames):
    """Randomly sample a part of the mel spectrogram."""
    r_idx = np.random.randint(0, high=mel_spec.shape[0] - n_frames + 1)
    return mel_spec[r_idx:r_idx + n_frames]

def prepare_trainset(dataset_name):
    f = h5py.File(common.PATCHES_DIR+'/patches_%s_%sx%s.hdf5' % (dataset_name,N_SAMPLES,SECONDS),'w')
    spec_folder=common.DATA_DIR+'/spectro_%s/' % SPECTRO_DATASET
    items = open(common.DATASETS_DIR+'/items_index_train_%s.tsv' % dataset_name).read().splitlines()
    factors = np.load(common.DATASETS_DIR+'/item_factors_%s_%s.npy' % (Y_PATH,dataset_name))
    n_items = len(items) * N_SAMPLES
    x_dset = f.create_dataset("features", (n_items,1,N_FRAMES,N_BINS), dtype='f')
    y_dset = f.create_dataset("targets", (n_items,factors.shape[1]), dtype='f')
    i_dset = f.create_dataset("index", (n_items,), dtype='S18')
    n=0
    k=0
    for t,track_id in enumerate(items):
        msd_folder = track_id[2]+"/"+track_id[3]+"/"+track_id[4]+"/"
        file = spec_folder+msd_folder+track_id+".pk"
        spec = pickle.load(open(file))
        spec = librosa.logamplitude(np.abs(spec) ** 2,ref_power=np.max).T
        for i in range(0,N_SAMPLES):
            try:
                sample = sample_patch(spec,N_FRAMES)                
                x_dset[k,:,:,:] = sample.reshape(-1,sample.shape[0],sample.shape[1])
                y_dset[k,:] = factors[t]
                i_dset[k] = track_id
                k+=1
            except Exception as e:
                print 'Error',e
                print file
        n+=1
        if n%100==0:
            print n

def prepare_testset(dataset_name):
    spec_folder=common.DATA_DIR+'/spectro_%s/' % SPECTRO_DATASET
    test_folder=common.DATA_DIR+'/spectro_%s_testset/' % SPECTRO_DATASET
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)
    items = open(common.DATASETS_DIR+'/items_index_test_%s.tsv' % dataset_name).read().splitlines()
    for t,track_id in enumerate(items[:10]):
        msd_folder = track_id[2]+"/"+track_id[3]+"/"+track_id[4]+"/"
        file = spec_folder+msd_folder+track_id+".pk"
        spec = pickle.load(open(file))
        spec = librosa.logamplitude(np.abs(spec) ** 2,ref_power=np.max).T
        pickle.dump(spec, open(test_folder+track_id+".pk","wb"))
        if t%1000==0:
            print t


if __name__ == '__main__':
    prepare_trainset(DATASET_NAME)
    prepare_testset(DATASET_NAME)
