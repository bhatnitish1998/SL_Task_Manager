# Software Lab Project : Task manager

## Statement
Monitoring system resource usage and performance metrics per process is a cumbersome task. A user-friendly GUI interface that would also generate statistics would be useful for the average user.

## Features
- [ ] A user-freindly interface which displays CPU usage (overall, per core, idle % ), Memory usage, Network usage, Disk usage etc.
- [ ] An End Task option to selectively kill processes.
- [ ] Alert user of High resource consuming processes.
- [ ] Generate reports periodically.


## Resources
- [Doc](https://docs.google.com/document/d/1cMxoMP7DjEBXepvbpFIOmppGlXQKzG7Tybeun3GM0uo/edit?usp=sharing)

## Tasks
- [ ] UI
    - [ ] Qt design
    - [ ] Data filling Pid table
    - [ ] Graph
- [ ] Data collection interface
    - [ ] Generate report/snapshot
    - [ ] Data Collection
    - [ ] Process information
    - [ ] Resource status : file/DB?

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
