# Peak Tracker

Documentation is currently a work in progress. But, program should be relatively intuitive to use at this point without every feature listed. Run the 'run.py' program to start Peak Tracker. Then proceed to select a folder that contains all the relevant tdms files as the import folder. The export folder will default to creating a new folder in your local Documents directory.

After you have data imported, you can select it manually. Left click to select a point where the Lorentzian's peak is. Right click and drag to select default amplitude and width parameters. Press space to commit your selection and it should turn green. Press enter/return when you're ready to start tracking.

To edit any of the tracking, fitting, export, debugging, or any other criteria, tweak them in 'modularConfig.py' These _will_ ultimately all be documented in full. But, we're not quite there yet I'm afraid.