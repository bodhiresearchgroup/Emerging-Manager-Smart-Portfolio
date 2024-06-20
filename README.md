# emerging_managers_project

Algorithm for classifying emerging managers. For additional context, [Ranjan's presentation.](https://drive.google.com/file/d/1wgCMWrMdHSyIR8qijBLeFdekC_snpbPq/view?usp=sharing)

## Current list of managers:
- PlusPlus
- Castlefield Associates
- DCM Systematic
- Mulvaney
- Teza (Microstructure)
- Teza (Systematic Futures)
- Rosetta (RL One)
- Rosetta (DL One)
- Panview
- Machina (Neutron)
- Trident (GME)
- Breakout
- Landscape
- Varick Capital

Note: Data last updated to 2024-01-01 by Aarya for all managers in list, except:
- panview only updated to 2023-07-01 -- we were kicked off the mailing list.
- varick only updated to 2023-08-01 -- no newer emails in research inbox.

## Key Steps
1. Initialize the algorithm.
    1. Parse timeseries data (month, rate of return) for each Manager.
    2. Perform various statistical calculations on all Managers and assign them scores for each statistical attribute.
2. For each Manager, create a group of peers
    1. A Manager's peers are other Managers with highly correlated timeseries
    2. TODO: assign a weighted score, based on statistical attributes, for the Manager and each of its peers (Note: done by Clara?)
    3. TODO: normalize the weighted score to create a weighted timeseries for each Manager in the group (Note: done by Clara?)
3. TODO: final set of weighted timeseries for all Managers is the output of the program.
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
