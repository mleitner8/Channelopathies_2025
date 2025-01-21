# Channelopathies_2024
Channelopathies Project - M1 model with detailed PT5B cell to model channelopathies.

First Step: Go to the folder `/sim` and write `nrnivmodl ../mod` to compile the mod files so simulations can run directly from that folder. \
Second Step: Now you are able to run the sims! \
Some important caveats: \
        1. In cfg.py we have a variable cfg.UCDAVIS = False. This variable allow us to switch between the UCDavis PT model and the model from the M1 original network. The way it is implemented right now (because of lack of time) is that they both load the same weight normalization file. Thus, if you switch between the two models, that should be taken into account. Everything is calibrated for the original PT cell, if you wish to use the new one, you have to run the weight normalization protocol.\
        2. The other important parameter is PTNaFactor which multiplies the sodium conductance in the entire cell, to model the loss of sodium channels in the mutated PT cell. Thus, we use PTNaFactor=1 for the original cell and PTNaFactor=0.5 for the mutated.\
        3. In the batch script, the simulations that is running is the custom(), with the grid search for the parameters of interest. You need to adapt the setRunCfg() function (it is located almost at the end of the file) to your interest. Specially the name of the log file. And if you want to run another of the options, for example mpi_direct or bulletin, check that the script file used is init.py and not a different one.

