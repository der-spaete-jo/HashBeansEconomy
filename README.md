This branch contains the newest version of the OutputHandler. New improvements of the OutputHandler are commited to this branch. If they are tested and working the branch can be merged into e.g. adaptive_pricing.

Notes:
 - is it really necessary to create files for data on the agent level
 - better save it in (more efficient) np arrays and only create files on the economy level
 - then if data on agent level is needed it can still be written to a file after the model run
