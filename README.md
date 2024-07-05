# emerging_managers_project

Algorithm for classifying emerging managers. For additional context, [Ranjan's presentation.](https://drive.google.com/file/d/1wgCMWrMdHSyIR8qijBLeFdekC_snpbPq/view?usp=sharing)

## Current list of managers:
- Aegeri Capital
- Breakout
- Castlefield Associates
- DCM Systematic
- Landscape
- Machina (Neutron)
- Mulvaney Capital 
- Panview
- PlusPlus Global Alpha
- Pula Capital
- Rosetta (DL One)
- Rosetta (RL One)
- Teza (Microstructure)
- Teza (Systematic Futures)
- Trident (GME)

To be added:
- Bastion Asset Management 
- Deep Field Capital (multiple strategies?)
- III Capital (equity market-neutral program) (data unknown)
- Tc43 LLC (data unknown)

Note: Data last updated to 2024-05-01 by Sharon for all managers in list. Old manager .csv's that are no longer of interest are stored in the 'Old data' folder.

## Key Steps
1. Initialize the algorithm.
    1. Parse timeseries data (month, rate of return) for each Manager.
    2. Perform various statistical calculations on all Managers and assign them scores for each statistical attribute.
2. For each Manager, create a group of peers
    1. A Manager's peers are other Managers with highly correlated timeseries
    2. Assign a weighted score, based on statistical attributes, for the Manager and each of its peers
    3. Normalize the weighted score to create a weighted timeseries for each Manager in the group
3. Final set of weighted timeseries for all Managers is the output of the program.
4. TODO: How well does the weighted set of Managers perform? Backtest. Should we tweak the weighting, the statistical operations, etc? 

## 1. Initializing the algorithm
`ManagerUniverse.py` is the main file for our algorithm, and the one that is initially run. It calls other files to parse the data, create the managers, and perform the statistical calculations for each manager. It outputs the final result.

### Parsing timeseries data
`ManagerUniverse.py` calls `Dataparser.py` to parse the timeseries CSVs in the `manager_returns` directory. Each timeseries CSV **_must_** adhere to a specific header format, datetime format, and contain no missing values. Details are in the header for `Dataparser.py`.

`Dataparser.py` returns the associated timeseries information. Specific details are in `Dataparser.get_timeseries`, as well as `Entities.py`.

### Creating managers
After parsing the timeseries, `ManagerUniverse.py` creates Manager entities and adds them to the simulation. A Manager entity class contains information about the manager, as well as the output of each statistical operation run on the manager. Additional details for the Manager entity are in `Entities.py`. 

`ManagerUniverse.py` creates Manager entities in `populate_managers`. Now we have everything to begin the statistical calculations.

### Performing statistical operations
In `ManagerUniverse.perform_manager_stats_calculations`, we call various functions in `StatsCalculations.py` to get the results of the statistical calculations for each manager. 

## 2. Creating Manager groups
After `populate_managers` and `perform_manager_stats_calculations`, `ManagerUniverse.py` starts by creating the highly correlated Manager groups (called clusters) in `populate_clusters`.

## Downloading the code
Working on the code using your local machine:
1. Download and open GitHub desktop 
2. Clone this repository 
3. Click 'Open the project in your external editor' (e.g., VSCode)
4. Set up a virtual environment for this project. 
5. Create your own branch and make all edits there. Don't push to main.

## Running UI
Note: Pula Capital.csv and Aegeri Capital.csv currently trigger edge cases that result in runtime errors. Move them out of the data folder before attempting to run the code, but DON'T push this change.
How to run:
1. Open terminal
2. Activate virtual environment
3. cd folder path (C:...\GitHub\emerging_managers_project)
4. run code: streamlit run UI_EMP.py

## Current Bugs & Issues
1. Undefined behaviour when omega score/sharpe ratio/drawdown cannot be calculated for a manager.
2. Undefined behaviour when a manager does not have enough data within the given date range.
3. Manager entity seems to be storing funds, not managers (i.e., one manager can have two Manager objects for two funds).
4. No documentation for 'test_timeseries' instance attribute in Manager class. Usage unclear.
5. Undefined behaviour when the correlation value given to ManagerUniverse is too large (i.e., no Managers are correlated, resulting in no clusters).
6. Do we want to find the weighted sum of all managers/funds in the dataset or the weighted sum within clusters? Our algorithm is doing the former.

## TODO
- Implement new metrics to measure the managers' performance.
- Implement new ways to display the data/results.
- Implement functionality that allows the user/coder to specify which datasets to use. Potential extensions: random dataset generator, filter datasets based on different properties, etc.
- Fix flagged errors (Sharon will do this).

## Notes
- Comments marked 'Flagged' indicate errors found within the code that need to be fixed/accounted for.
- Comments marked 'Prev:' indicate comments left by the previous authors of the code.