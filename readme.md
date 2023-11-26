# Software Lab Project : Task manager

## Statement
Monitoring system resource usage and performance metrics per process is a cumbersome task. A user-friendly GUI interface that would also generate statistics would be useful for the average user.

## Features
- [x] A user-freindly interface which displays CPU usage (overall, per core, idle % ), Memory usage, Network usage, Disk usage etc.
- [x] An End Task option to selectively kill processes.
- [x] Alert user of High resource consuming processes.
- [x] Generate reports periodically.

## How to run locally
- download the repo and cd to roo directory
- install dependencies
    - `pip install -r requirements.txt`
    - install latex dependencies
        - ubuntu `sudo apt install texlive`
        - arch `sudo pacman -S texlive-latex`
- do `python main.py`
```bash
git clone git@github.com:bhatnitish1998/SL_Task_Manager.git
cd SL_Task_Manager
pip install -r requirements.txt
sudo apt install texlive
python main.py
```


## Resources
- [Doc](https://docs.google.com/document/d/1cMxoMP7DjEBXepvbpFIOmppGlXQKzG7Tybeun3GM0uo/edit?usp=sharing)

## Tasks
- [x] UI
    - [x] Qt design
    - [x] Data filling Pid table
    - [x] Graph
- [x] Data collection interface
    - [x] Generate report/snapshot
    - [x] Data Collection
    - [x] Process information

## Project structure (subject to change)
```
UI/
	Xml
	Py file to populate
	resources/
DATA/
	Bash scripts pid.sh, resource.sh
    Python bash interface
	File
Main.py
	Func to call ui_py
```
