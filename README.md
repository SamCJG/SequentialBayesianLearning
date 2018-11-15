# Sequential Bayesian Learning
## Author: Robert Tjarko Lange, Miro Grundei, Sam Gjisem
## Date: November 2018

Repository implements different Sequential Bayesian Learning Agents which parse a binary sequence. The binary sequence was previously generated by a Hierarchical Hidden Markov Model.
As the agent parses the individual elements of the sequence she updates her posterior and calculates surprisal measures (Predictive, Bayesian and Confidence-Corrected):

![Alt text](pics/sbl_bb.gif)

The agents include the following:

* Beta-Bernoulli (BB) agent
* Gaussian Random Walk (GRW) agent
* Gaussian Hierarchical Filter (GHF) agent

The models include the following:

* [x] BB agent modeling the stimulus probability (SP)
* [x] BB agent modeling the alternation probability (AP)
* [x] BB agent modeling the transition probability (TP)
* [x] GRW agent modeling the stimulus probability (SP)
* [x] GRW agent modeling the alternation probability (AP)

TODO:

* [ ] GRW agent modeling the transition probability (TP)
* [ ] GHF agent modeling the stimulus probability (SP)
* [ ] GHF agent modeling the alternation probability (AP)
* [ ] GHF agent modeling the transition probability (TP)
* [ ] Change generation process to include 2nd order Markovity and catch trials
* [ ] Add passing of input file in hhmm_seq_gen format
* [ ] Clean up visualization pipeline

## Repository Structure
```
SequentialBayesianLearning
+- hhmm_seq_gen.py: Contains HHMM that samples a binary sequence.
+- sbl_bb.py: Contains Beta-Bernoulli learner for different models
+- sbl_grw.py: Contains Gaussian Random Walk learner for different models
+- visualize.py: Runs gif visualization of learning
+- pics: contains visualizations of results
+- results: contains txt files with suprisal/sequence
+- README.md: Project Documentation
+- requirements.txt: list of all required pip packages
```

## How to use this code
1. Clone the repo.
```
git clone https://github.com/RobertTLange/SequentialBayesianLearning && cd SequentialBayesianLearning
```
2. Create a virtual environment (optional but recommended).
```
virtualenv -p python SBL
```
Activate the env (the following command works on Linux, other operating systems might differ):
```
source SBL/bin/activate
```
3. Install all dependencies:
```
pip install -r requirements.txt
```
4. Run the different sequential learning agents (e.g. for a seq with length 200):
```
python mmn_sbl.py -model SP
python mmn_sbl.py -model AP
python mmn_sbl.py -model TP
```

* Arguments:
    * -S: to save the results in a txt file
    * -T: run a few tests to check if module is working
    * -reg_init: Initial regime probability
    * -reg_change: Probability of changing regimes
    * -obs_init: Initial regime probability
    * -obs_change', '--prob_obs_change', action="store", default=0.25, type=float,
						help="Probability of changing regime")
    parser.add_argument('-seq', '--sequence_length', action="store", default=200, type=int,
						help='Length of binary sequence being processed')
    parser.add_argument('-tau', '--forget_param', action="store", default=0., type=float,
                        help='Exponentially weighting parameter for memory/posterior updating')
    parser.add_argument('-model', '--model', action="store", default="SP", type=str,
                        help='Beta-Bernoulli Probability Model (SP, AP, TP)')
