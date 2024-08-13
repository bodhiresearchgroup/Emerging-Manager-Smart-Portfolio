# emerging_managers_project

Algorithm for classifying emerging managers. For additional context, [Ranjan's presentation.](https://drive.google.com/file/d/1wgCMWrMdHSyIR8qijBLeFdekC_snpbPq/view?usp=sharing)

## UPDATES (Aug 12)
1. The algorithm has been modified to include a larger dataset, with clusters being formed only around a subset of core programs (see list below). Non-core programs are located in the folder `Old data`.
2. The scoring system of the algorithm has been modified to give each core program a score from 1-3, with 3 being the best. The weight for each program is calculated using this score, normalized.
3. `main.py` has been added for modularization. Namely, `calculate_metrics` and `Portfolio_Performance` have been moved from `ManagerUniverse.py`. The main algorithm in `UI_EMP.py` has also been moved to `main.py`. 
4. The main algorithm logic has been changed. For more information, see the function docstrings of `Static_Performance` and `Iterative_Performance` in `main.py`. As discussed with Ranjan, we will be using the `Static_Performance` method for now. 
5. Major flagged errors have been resolved. All core programs in the `Data` folder can now be included when running the UI.
6. The `Timeseries` class has been refactored to hold data in a pd.Series instead of two lists for memory efficiency, indexing, etc.
7. Tests for `StatsCalculations.py` have been added. Tests are being run on `Test Manager.csv` in the `tests` folder. 

## TODO
- Modify the way we calculate drawdown (area instead of max). 
- Write tests for any functions you write. Start with StatsCalculations.py. Create new datasets to test on if necessary.
- Determine edge case behaviour:
    - Omega ratio can't be calculated in time periods with no negative returns.
    - How to handle clusters containing only 1 program. (Should we enforce min cluster size?)
    - How to handle case where drawdown never recovers?
    - etc.
- Implement new metrics to measure the programs' performance.
- Implement new ways to display the data/results.
- Implement functionality that allows the user to specify which datasets to use. Potential extensions: random dataset generator, filter datasets based on different properties, etc.

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

Note: Data last updated to 2024-05-01 by Sharon for all programs in above list. 

## Key Steps
1. Initialize the algorithm.
    1. Parse timeseries data (month, rate of return) for each Program.
    2. Perform various statistical calculations on all Programs and assign them a score based on each statistical attribute.
2. For each Program, create a group of peers
    1. A Program's peers are other Programs with highly correlated timeseries
3. Assign a score, based on statistical attributes, for each Program 
    1. Normalize the score to create a weight that will be applied to each Program's timeseries.
    2. Sum each weighted timeseries to get a single portfolio. This is the output of the program.
4. Display the results
5. TODO: How well does the weighted set of Programs perform? Backtest. Should we tweak the weighting, the statistical operations, etc? 

## 1. Initializing the algorithm
`ManagerUniverse.py` is the main file for our algorithm, and the one that is initially run. It calls other files to parse the data, create the Programs, and perform the statistical calculations for each program. It outputs the final result.

### Parsing timeseries data
`ManagerUniverse.py` calls `Dataparser.py` to parse the timeseries CSVs in the `Data` directory. Each timeseries CSV **_must_** adhere to a specific header format, datetime format, and contain no missing values. Details are in the header for `Dataparser.py`.

`DataParser.py` returns the associated timeseries information. Specific details are in `DataParser.get_timeseries`, as well as `Entities.py`.

### Creating Program objects
After parsing the timeseries, `ManagerUniverse.py` creates Program entities and adds them to the simulation. A Program entity class contains information about the program, as well as the output of each statistical operation run on the program. Additional details for the Program entity are in `Entities.py`. 

`ManagerUniverse.py` creates Program entities in `populate_programs`. Now we have everything to begin the statistical calculations.

### Performing statistical operations
In `ManagerUniverse.perform_program_stats_calculations`, we call various functions in `StatsCalculations.py` to measure the performance of each program. 

## 2. Creating Program groups
`ManagerUniverse.py` starts by creating the correlated Program groups (called Clusters) in `populate_clusters`.

## 3. Assigning weights
`ratings_df` goes through each cluster and assigns scores to each program based on its performance relative to its cluster peers. These scores are normalized so that we can create a single weighted timeseries from the dot product of the scores and original timeseries of each program.

### Creating a weighted timeseries
The 3 methods under the comment `# Weighted Portfolios` in `ManagerUniverse.py` perform the multiplication between weights and timeseries for each program. Each function uses different weights; see docstrings for more info. 

## 4. Running the main algorithm
The entry point of the application is located in `main.py`. Functions in this file call the various helper functions and modules described above to execute the algorithm from start to finish. 

## 5. Displaying the results
The final results from `main.py` are displayed in `UI_EMP.py` using Streamlit. 

### Running UI
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

## Current Bugs & Issues
1. Undefined behaviour when omega score/sharpe ratio/drawdown cannot be calculated for a program.
2. Undefined behaviour when a program does not have enough data within the given date range.
3. Undefined behaviour when the correlation value given to ManagerUniverse is too large (i.e., no Programs are correlated, resulting in no clusters).

### Notes
- Comments marked 'Flagged' indicate errors found within the code that need to be fixed/accounted for.
- Comments marked 'Prev:' indicate comments left by the previous authors of the code.