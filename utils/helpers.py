import os
import pickle
from scipy import log, log2, array, zeros
import scipy.io as sio
from scipy.special import gamma, digamma, gammaln
from scipy.stats import dirichlet

import numpy as np

results_dir = os.getcwd() + "/results/"


def save_obj(obj, title):
    with open(title + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(title):
    filename, file_extension = os.path.splitext(title)
    if file_extension == ".mat":
        out = sio.loadmat(title)
        sample = out["C"][0][0][5][0][0][0]
        meta = {}
        meta["prob_obs_init"] = out["C"][0][0][5][0][0][1]
        meta["prob_regime_init"] = out["C"][0][0][5][0][0][2]
        meta["prob_obs_change"] = out["C"][0][0][5][0][0][3]
        meta["prob_regime_change"] = out["C"][0][0][5][0][0][4]
        return sample, meta
    else:
        with open(title, 'rb') as f:
            return pickle.load(f)


def kl_general(p, q):
    """Compute the KL divergence between two discrete probability distributions
    The calculation is done directly using the Kullback-Leibler divergence,
    KL( p || q ) = sum_{x} p(x) ln( p(x) / q(x) )
    Natural logarithm is used!
    """
    if (p==0.).sum()+(q==0.).sum() > 0:
        raise "Zero bins found"
    return (p*(np.log(p) - np.log(q))).sum()


def kl_dir(alphas, betas):
    """Compute the KL divergence between two Dirichlet probability distributions
    """
    alpha_0 = alphas.sum()
    beta_0 = betas.sum()

    a_part = gammaln(alpha_0) - (gammaln(alphas)).sum()
    b_part = gammaln(beta_0) - (gammaln(betas)).sum()

    ab_part = ((alphas - betas)*(digamma(alphas) - digamma(alpha_0))).sum()
    return a_part - b_part + ab_part


def draw_dirichlet_params(alphas):
    if len(alphas) != 8:
        raise ValueError("Provide correct size of concentration params")
    return np.random.dirichlet((alphas), 1).transpose()


def stand(surprise):
    # Standardize surprise arrays
    arr = np.array(surprise)
    temp = arr/np.nanmax(arr, axis=0)
    return temp


def preproc_surprisal(SP, AP, TP):
    time = SP["time"]
    hidden = SP["hidden"]
    sequence = SP["sequence"]

    PS = [stand(SP["predictive_surprise"]),
          stand(AP["predictive_surprise"]),
          stand(TP["predictive_surprise"])]
    BS = [stand(SP["bayesian_surprise"]),
          stand(AP["bayesian_surprise"]),
          stand(TP["bayesian_surprise"])]
    CS = [stand(SP["confidence_corrected_surprise"]),
          stand(AP["confidence_corrected_surprise"]),
          stand(TP["confidence_corrected_surprise"])]

    return time, hidden, sequence, PS, BS, CS


def get_electrode_data(eeg_data, block_id, elec_id):
    num_blocks = 5
    num_trials = 4000
    # Subselect eeg and recording time stamps from raw data object in .mat file
    """
    Structure of eeg_raw/eeg_times object: Sampling rate of 512 points per second
        - raw: Num rows = number of blocks, Num cols = Number of electrodes (see EOI)
        - times: Num rows = number of trials and start of blocks (last rows)
    """
    eeg_raw = eeg_data["data"][0]
    eeg_time = eeg_data["data"][1]
    # Select data according to block and electrode id
    elec_bl_raw = eeg_raw[block_id][elec_id]
    eeg_bl_time = eeg_time[block_id].flatten()

    # Select block-specific event times from from raw data in .mat file
    """
    Structure of event_times object: Rows 1-4000: Events/Trials
        First Col: Boolean for Bad Quality Trial
        Second Col: Form of stimulus/trial see trial_coding_lookup object
        Third Col: Time of trial - use to match with elec_bl_raw to get data

    block_start_times: Final rows of event_times yield the starting times of blocks
        - use to subselect specific data with the help of the trial times
    """
    event_times = eeg_data["event_times"][0]
    event_times = np.array(event_times.tolist()).reshape((num_trials+num_blocks, 3))
    block_start_times = []

    for i in range(len(event_times[num_trials:])):
        block_start_times.append(event_times[num_trials:][i][2])
    # Append final point in time and sanity check
    block_start_times.append(event_times[num_trials-1][2])
    if len(block_start_times) != (num_blocks + 1):
        raise "Something is wrong with data shape: Wrong number of blocks!"

    time_int = block_start_times[block_id:block_id+2]
    start_idx = np.where(event_times[:, 2] > time_int[0])
    stop_idx = np.where(event_times[:, 2] < time_int[1])
    block_event_idx = np.intersect1d(start_idx, stop_idx)
    # Select event times based on start/stop of block
    events_in_block = event_times[block_event_idx, 2]
    if len(events_in_block) != (num_trials/num_blocks):
        raise "Something is wrong with data shape: Wrong number of events!"

    # Select raw eeg data based on block-specific event times - Get closest point!
    # This is ultimately the data we want to explain in our analysis
    tree = KDTree(events_in_block)
    neighbor_dists, neighbor_indices = tree.query(eeg_bl_time)
    _, data_idx = np.unique(neighbor_indices, return_index=True)
    eeg_data_out = elec_bl_raw[data_idx]
    return eeg_data_out
