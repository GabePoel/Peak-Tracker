# Peak Tracker

Documentation is currently a work in progress. But, program should be relatively intuitive to use at this point without every feature listed. Run the 'run.py' program to start Peak Tracker. Then proceed to select a folder that contains all the relevant tdms files as the import folder. The export folder will default to creating a new folder in your local Documents directory.

After you have data imported, you can select it manually. Left click to select a point where the Lorentzian's peak is. Right click and drag to select default amplitude and width parameters. Press space to commit your selection and it should turn green. Press enter/return when you're ready to start tracking.

To edit any of the tracking, fitting, export, debugging, or any other criteria, tweak them in 'modularConfig.py' These _will_ ultimately all be documented in full. But, we're not quite there yet I'm afraid.

## Quick Start Guide

Peak Tracker comes with a pre-loaded set of data to experiment with before plugging in your own. Before you load up your own RUS data and get frustrated trying to figure out how to make Peak Tracker work, it's recommended that you follow along with this guide which goes through the basics of how to use Peak Tacker with this initialized default data.

To start Peak Tracker, run the 'run.py' file in the Peak-Tracker directory. It should pull up a window that looks something like the following. The interface is made using TkInter and the exact look/feel will vary depending on your OS and desktop environment.

![Blank Window](https://raw.githubusercontent.com/GabePoel/Peak-Tracker/master/images/blankWindow.png)

From here you can either load your own data or use the latest saved/pre-loaded data. To load the current set of data, press the cleverly named 'Load Data' button. If you haven't previously set a directory to load data from, Peak Tracker will just use the default set of data. You can set a new import directory to load your data from by clicking the cleverly named 'Set Import' button. If you do so, a window like the following should pop up.

![Directory Selection Window](https://raw.githubusercontent.com/GabePoel/Peak-Tracker/master/images/activeDirectory.png)

From here you should navigate to the directory that contains the tdms data you want to analyze. That directory (not open in the selection window) should look something like this.

![tdms Directory](https://raw.githubusercontent.com/GabePoel/Peak-Tracker/master/images/tdmsDirectory.png)

Of course, for your first time running Peak Tracker, you can just leave the default directory and don't have to click 'Set Import' at all.

Assuming you've now loaded the default data set, you should have a window that looks something like the following.

![Window with Loaded Data](https://raw.githubusercontent.com/GabePoel/Peak-Tracker/master/images/loadedWindow.png)

From here you can explore your data in a couple ways. Clicking 'Quick Display' will show the in-phase, out-of-phase, and quadrature components of the frequency data at the first recorded temperature.

![Quick Display Window](https://raw.githubusercontent.com/GabePoel/Peak-Tracker/master/images/quickDisplay.png)

For a qualitative sense of how messy your data is, you can click on 'See Background' to see the in-phase and out-of-phase components plotted against each other.

![See Background](https://raw.githubusercontent.com/GabePoel/Peak-Tracker/master/images/background.png)

When you're ready to detect the Lorentzian spikes in your frequency data, click on 'Detect Peaks.' This tells Peak Tracker to look for peaks through whatever means is currently configured (see Configuring for Your Data). By default, Peak Tracker has you manually trace out and select the peaks used in the detection. This is because the automatic detection does not currently work. But, we can still dream of a future where it does. Upon clicking 'Detect Peaks' the same data initially loaded should appear, but it should now be black. Don't worry, this is just a visual clue to say that the program is waiting for your input. It doesn't mean anything scary is about to happen.

![Unselected Peak Detection Window](https://raw.githubusercontent.com/GabePoel/Peak-Tracker/master/images/peakDetectionWindow.png)

Now that the manual peak detection interface is open, you should be able to go ahead and start selecting peaks of your Lorenztians and start tracign out their forms. But before you do so, note that there exists a small bug on some systems where the detection freezes partway through the selection process for some reason. This seems to be an issue with matplotlib and not with Peak Tracker. To avoid this, just move your cursor around in the plotted window for a few seconds. If the crosshairs stop moving, then click 'Detect Peaks' again. If you can wiggle the cursor for a while without the crosshairs stopping, then everything should be good to go. Depending on your system and how you're running Peak Tracker, it may take several attempts to work properly.

![One Complete Selection](https://raw.githubusercontent.com/GabePoel/Peak-Tracker/master/images/oneSelectionWindow.png)

To start your selection process, use the matplotlib window interface controls un the upper left to zoom in around the Lorentzians you're interested in tracking. Left click the peak of the Lorentzian and then right click and drag to select a region around it. This should show up as a red 'x' at the peak and a dashed line around the area that's selected. This provides the initial guess for the frequency, amplitude, and full width half maximum of the Lorentzian. Note that depending on the method that the least squares reduction uses to select the box constraints you may need a slightly wider or narrower selection region. In general, when the selection method is configured to 'dogbox' a narrower region is needed. Don't worry too much about this though, you'll quickly get a feel for it when selecting.

Once you've made your initial selection, press the spacebar to commit it. This will turn your selection region green and show the Lorentzian that Peak Tracker tried to fit over your region. You can also click 'Save Current Peaks' at any time to have Peak Tracker remember the peaks you've selected in case you want to run the fitting/tracking process again with different parameters configured.

![One Complete Detection](https://raw.githubusercontent.com/GabePoel/Peak-Tracker/master/images/oneDetectionWindow.png)

If Peak Tracker fits a curve that's incorrect or that you just don't like the look of, press the backspace key. This removes whatever the last selection made was. You can do this at any point during the selection process. If you want to see what commands are currently available (as well as some of the other manual detection debugging tools), press the 'q,' 'w,' and/or 'e' keys. The current state of different aspects of the detection process should pop up in your terminal window.

Once you've selected/detected all the peaks that you want to look at, go ahead and press the enter key. This will tell Peak Tracker to start processing your data given the initial conditions you've set.

![A Full Detection Set](https://raw.githubusercontent.com/GabePoel/Peak-Tracker/master/images/fullDetection.png)

Depending on your configuration, you may now see a live display of Peak Tracker fitting over each temperature of your data. The blue curve is the data itself, the red curves are the fitted Lorentzians, the green 'x' points are the predicted peaks, and the yellow curve is the noise filtering region. All of this is explained in more detail under Data Control Features.

![A Live Fitting Process](https://raw.githubusercontent.com/GabePoel/Peak-Tracker/master/images/trackingProcess.png)

Once the tracking process is done, depending on your configured settings, you may have a plot like the following appear.

![Results of Tracking Process](https://raw.githubusercontent.com/GabePoel/Peak-Tracker/master/images/trackingResult.png)

This is a visualization of the peak location in frequency space as a function of temperature. It should also be saved in your export directory.

By default, Peak Tracker will create a new export directory in your Documents folder to save things in. But, you can also change where things get exported to by clicking 'Set Export.' Peak Tracker exports a bunch of different processed items for your review by default. But, you can configure these as you wish. See Export Features for more information on everything Peak Tracker does and does not currently export.

![Export Directory](https://raw.githubusercontent.com/GabePoel/Peak-Tracker/master/images/exportDirectory.png)

## Data Processing Features

TBD

## Export Features

TBD

## Configuring Your Data

TBD

## Overview

TBD