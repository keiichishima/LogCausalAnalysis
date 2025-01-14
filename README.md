# LogCausalAnalysis

## Overview

This project provides a series of functions to analyze 
system log data in terms of event causality.

* Classify log data with its output format
* Generate DAG with PC algorithm (using pcalg/gsq package)
* Process log incrementally and notify troubles <- work in progress

## Package requirements

* pcalg https://github.com/keiichishima/pcalg
* gsq https://github.com/keiichishima/gsq

## Tutorial

You can generate pseudo log dataset for testing functions.

$ python testlog.py > test.temp

First, you need to put a configuration file for whole system.
Copy default file, and edit it if necessary.

$ cp config.conf.default config.conf

Then classify dataset and register them with database.
Classification works with log template generation inside this command.

$ python log_db.py

You can see log templates found in log messages with following command.

$ python lt_edit.py show

If found log template do not make reasonable event group,
Following command may be useful.

$ python lt_edit.py [breakdown, merge, separate]

Finally analyze causal relations generating DAG.
(This step requires much time. If your machine have enough performance,
we recommend you to use -p options for multithreading.)

$ python pc_log.py

You can check result DAG with following command.

$ python pcresult.py -g graph.pdf pc_output/all_21120901

