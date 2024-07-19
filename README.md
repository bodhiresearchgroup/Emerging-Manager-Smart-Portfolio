# emerging_managers_project

Algorithm for classifying emerging managers. For additional context, [Ranjan's presentation.](https://drive.google.com/file/d/1wgCMWrMdHSyIR8qijBLeFdekC_snpbPq/view?usp=sharing)

## Important
The terms "manager" and "program" are currently used interchangeably in this project. Most of the time, we mean "program". The code is being refactored to reflect this.

## Current list of programs:
- Aegeri Capital
- Bastion Asset Management (BAM LS Equity Class M)
- Breakout
- Castlefield Associates (Global Systematic)
- DCM Systematic (Diversified Alpha)
- Landscape (Capital Partners)
- Machina (Neutron)
- Mulvaney Capital (Global Markets)
- Panview (Asian Equity)
- PlusPlus Capital (Global Alpha)
- Pula Capital
- Rosetta (DL One)
- Rosetta (RL One)
- Teza (Microstructure)
- Teza (Systematic Futures)
- Tc43
- Trident (GME)

To be added:
- Deep Field Capital (multiple strategies?)
- III Capital (equity market-neutral program) (hypothetical data?)

Note: Data last updated to 2024-05-01 by Sharon for all programs in list. Old program .csv's that are no longer of interest are stored in the 'Old data' folder.

## Key Steps
1. Initialize the algorithm.
    1. Parse timeseries data (month, rate of return) for each Program.
    2. Perform various statistical calculations on all Programs and assign them scores for each statistical attribute.
2. For each Program, create a group of peers
    1. A Program's peers are other Programs with highly correlated timeseries
3. Assign a weighted score, based on statistical attributes, for each Program 
    1. Normalize the weighted score to create a weighted timeseries for each Program 
    2. Sum each weighted timeseries to get a single timeseries based on the weights among all Programs. This is the output of the program.
4. Display the results
5. TODO: How well does the weighted set of Programs perform? Backtest. Should we tweak the weighting, the statistical operations, etc? 

## 1. Initializing the algorithm
`ManagerUniverse.py` is the main file for our algorithm, and the one that is initially run. It calls other files to parse the data, create the Programs, and perform the statistical calculations for each program. It outputs the final result.

### Parsing timeseries data
`ManagerUniverse.py` calls `Dataparser.py` to parse the timeseries CSVs in the `manager_returns` directory. Each timeseries CSV **_must_** adhere to a specific header format, datetime format, and contain no missing values. Details are in the header for `Dataparser.py`.

`Dataparser.py` returns the associated timeseries information. Specific details are in `Dataparser.get_timeseries`, as well as `Entities.py`.

### Creating Program objects
After parsing the timeseries, `ManagerUniverse.py` creates Program entities and adds them to the simulation. A Program entity class contains information about the program, as well as the output of each statistical operation run on the program. Additional details for the Program entity are in `Entities.py`. 

`ManagerUniverse.py` creates Program entities in `populate_managers`. Now we have everything to begin the statistical calculations.

### Performing statistical operations
In `ManagerUniverse.perform_manager_stats_calculations`, we call various functions in `StatsCalculations.py` to get the results of the statistical calculations for each program. 

## 2. Creating Program groups
After `populate_managers` and `perform_manager_stats_calculations`, `ManagerUniverse.py` starts by creating the highly correlated Program groups (called clusters) in `populate_clusters`.

## 3. Assigning weights
`ratings_df` goes through each cluster and assigns scores to each program based on its performance relative to its cluster peers. These scores are normalized so that we can create a single weighted timeseries from the dot product of the scores and original timeseries of each program.

### Creating a weighted timeseries
The 3 methods under the comment `# Weighted Portfolios` in `ManagerUniverse.py` perform the multiplication between weights and timeseries for each program. Each function uses different weights; see docstrings for more info. Note that this section will be refactored because it contains duplicate code. 

Finally, `Portfolio_Performance` sums each weighted timeseries to create a single timeseries and calls `calculate_metrics` to obtain various statistics. 

## 4. Displaying the results
The final results are displayed in `UI_EMP.py`. This is also where all of the methods described above are called. It's currently being done in a way that I (Sharon) am mildly confused about; in particular, the for loop. Interpret the code how you will and we will regroup to discuss.

### Running UI
Note: Pula Capital.csv and Aegeri Capital.csv currently trigger edge cases that result in runtime errors. Move them out of the data folder before attempting to run the code, but DON'T push this change.
How to run:
1. Open terminal
2. Activate virtual environment
3. cd folder path (C:...\GitHub\emerging_managers_project)
4. run code: streamlit run UI_EMP.py

## Working On The Code
Before working on the code, please read the following [Guide to GitHub Workflow](https://docs.google.com/presentation/d/1ukgFfcJL5dy5sz1kGzME225qfhD_h5SC/edit?usp=sharing&ouid=100889947998135845452&rtpof=true&sd=true).

### Downloading the project onto your local machine:
1. Download and open GitHub Desktop 
2. Clone this repository 
3. Click 'Open the project in your external editor' (e.g., VSCode)
4. Set up a virtual environment for this project. 
5. Create your own branch and make all edits there. 

## TODO
- Modify the way we weigh drawdown. 
- Implement new metrics to measure the managers' performance.
- Implement new ways to display the data/results.
- Implement functionality that allows the user to specify which datasets to use. Potential extensions: random dataset generator, filter datasets based on different properties, etc.
- Fix flagged errors (Sharon will do this).

## Current Bugs & Issues
1. Undefined behaviour when omega score/sharpe ratio/drawdown cannot be calculated for a program.
2. Undefined behaviour when a program does not have enough data within the given date range.
3. No documentation for 'test_timeseries' instance attribute in Program class. Usage unclear.
4. Undefined behaviour when the correlation value given to ManagerUniverse is too large (i.e., no Programs are correlated, resulting in no clusters).

### Notes
- Comments marked 'Flagged' indicate errors found within the code that need to be fixed/accounted for.
- Comments marked 'Prev:' indicate comments left by the previous authors of the code.