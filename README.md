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

As it currently stands, the best way to customize/configure Peak Tracker for your individual data is to edit the 'modularConfig.py' file directly. Don't worry though, it should be hard to screw anything up _too_ badly. As of the time of writing this guide, opening the file should show something like the following:

```python
allowedLogUpdates = {"RATE_OF_CHANGE_PREDICTION": False, 
                     "AMPLITUDE_CORRECTION": True,
                     "SKEW_CORRECTION": True,
                     "WIDTH_CORRECTION": True,
                     "DEGENERACY_LOG": True,
                     "COST_LOG": False}
amplitudeGrowLimit = 10
amplitudeShrinkLimit = 10
backgroundSuppression = False
closeLorentzAmplitude = 1.2
closeLorentzFrequency = 0.5
closeLorentzSkew = 1.2
closeLorentzWidth = 1.2
curveFallBlocking = False
dataExportHeaders = True
defaultExportDirectory = "local"
defaultImportDirectory = "default"
detectionTechnique = "manual"
displayScale = "local"
enablePerturbations = True
exportConfig = True
exportDataComplex = False
exportDataSimple = True
exportDirectory = "default"
exportFinalTrends = True
exportImages = True
exportParameters = True
exportVideo = True
forceSingleLorentz = False
leastSquaresMethod = "dogbox"
liveUpdate = True
loadDirectory = "default"
multiFitLimit = 2
noiseFilterDisplay = True
noiseFilterLevel = 4
peakSeparationFactor = 50
peakPlotBackgroundColor = 'b'
peakPlotFitColor = 'r'
peakPlotPeakColor = 'g'
rateOfChangeLength = 50
rateOfChangeTracking = True
terminationCostTolerance = None
terminationGradientTolerance = None
terminationIndependentTolerance = 1e-15
widthExpansionBase = 1.8
widthExpansionRate = 1
widthGrowLimit = 1
widthShrinkLimit = 1
quickTracking = False
quickTrackingLength = 5
```

Each named variable corresponds to a different parameter/setting you can tweak to your specific Peak Tracker needs. They are aranged in alphabetical order and generally named such that associated parameters are grouped together. But, the naming scheme isn't _completely_ perfect. However, it still shouldn't be too hard to find what you need. Each parameter is explained briefly below.

### Lorentz Correction Factors

All of these parameters involve trying to catch and correct for cases when the initial least squares fit does not converge on the correct Lorentzian in the way that we want it to.

#### amplitudeGrowLimit

This determines the factor with which the detected Lorentzian is allowed to grow by between two neighboring temperatures. If the new fit grows far too much, then it's likely that the tracker converged to either the background or to a different Lorentzian. In such cases, the tracker reports the error and uses the predicted Lorentzian parameters instead for this and as a starting case for future fits.

#### amplitudeShrinkLimit

This is exactly the same as the `amplitudeGrowLimit` except that it determines the multiplicative factor with which a Lorentizan is allowed to shrink from one temperature to the next. Although the default has `amplitudeGrowLimit` and `amplitudeShrinkLimit` set to the same value, there exists cases where it's best to tune these separately.

#### backgroundSuppression

This is a prototype feature to try and detect the general background Lorentzians and subtract them from the overall data prior to fitting. It uses a different technique than that used for detecting the background noise level and doesn't work well with changing conditions. It's not recommended you set this to `True` as `backgroundSuppression` does not work well at this time.

#### curveFallBlocking

This enables an attempt at catching the rare cases where the least squares fit reports some incredibly aberant value and goes off the scale of our frequency data entirely. It _seems_ that this may be due to some obscure condition with sciPy's `least_squares` function. But, either way, the case is very rare (assuming parameters are configured relatively well) and `curveFallBlocking` generally causes more problems than it's worth. That is to say this feature is not functional nor worth using at this time.

#### enablePerturbations

Occasionally the least squares fit will get confused and converge on a piece of the background or just a small part of the Lorentzian even though the actual (and better) fit should be within the space of its search. This is to keep the least squares fit from getting stuck within a local minima by adding slight random perturbations to the predicted Lorentzian fit parameters and letting the fit run several times to take the best one. The tuning for the scale of these perturbations is not super functional currently, so it's not recommended that this feature be used at this time. If you do use it, be especially careful of densely packed Lorentzians.

#### widthGrowLimit

This is mostly analagous to `amplitudeGrowLimit`, but tends to be a little bit more finicky since its much easier for the least squares fit to see something of value within the background and gradually increase around the actual voltage spike until it almost exclusively captures the background. As such, it's recommended that you keep the `amplitudeGrowLimit` as low as possible. If you are only looking for the way the frequency at the peak of the Lorentzian changes, you should leave both `widthGrowLimit` and `widthShrinkLimit` at `1`. This prevents _any_ change in the width of the Lorentzian. This may sound harsh, but it is very effective in preventing the Peak Tracker from converging to something that isn't the actual Lorentzian that is intended to be tracked. Unlike the amplitude conditions, the width ones only correct the width of the reference Lorentzian and not its other parameters. As such, all the other physics is properly presented even if the limits are set at `1`.

#### widthShrinkLimit

See `widthGrowLimit`.

#### quickTracking

If you just want to briefly see how the parameters you configure work with the data you have, you should enable quickTracking. Instead of running Peak Tracker on your full data set, in only looks at a finite number of temperature points as determined by `quickTrackingLength`.

#### quickTrackingLength

This determines the number of temperature data points Peak Tracker analyzes while quick tracking. The data starts analyzing from the first temperature just as it does with a full tracking, but stops in finite time. This could also be helpful for getting a sense of how long Peak Tracker may take to run given your current configuration.

#### noiseFilterLevel

Noise filtering doesn't actually reduce the background noise of the given data. Instead, it looks at the tracked Lorentzians and determines if they shrink so much that they are at a scale such that they are indestinguishable from the backgroudn noise. Often times even if a Lorentzian could be easily made out by a human eye, the noise will be large enough that least square fit will converge on a value that includes some piece of the noise and just thinks the phase of the Lorentzian changed drastically. That's why the default noiseFilterLevel is set to the relatively high value of `4`.

The noise filter is built on the assumption that the level of background noise does not greatly change over the course of the given data. It works by first subtracting only the _initial_ peaks provided from the background at the first temperature data point. Assuming that the initial (manually confirmed) fits are relatively accurate, then post-subtraction the frequency regions in which they occured should be locally linear with only the background noise and perhaps a _very slight_ curve from the background shape remaining. As such, these regions can be treated just as linear regions with noise added and the noise level can be guessed at by taking the standard deviation of the values over this region. This standard deviation will inherently be a slight underestimate of the noise level, so it's worth having the noise filter be set to at least `2`. An alternative scheme involves taking the maximum of the noise levels and using that as the baseline noise filter prediction. If such a method is used, then `noiseFilterLevel` should be set higher since we will likely have a slight overestimate.

### Lorentz Prediction Factors

Some of these paramaters find the average rate of change of the last handful of fits and try to predict what the change for the new Lorenztian parameters will be. They then are applied to the reference/default parameters that the least square fit converges over.

#### rateOfChangeLength

This sets how many previous data points are looked over when determing the predicted values. If it's set too high then the weight of the prediction may overshadow the changes that occur from phase transitions. As such, Peak Tracker will search in the regions the Lorentzians might have been had the phase transition never occured.

#### rateOfChangeTracking

This enables or disables taking the rate of change into consideration when constructing the reference Lorentzian parameters.

#### widthExpansionBase

This determines the size of the area around the fitted Lorentzian that is used to search for others in new temperature values.

#### widthExpansionRate

Assuming that there is not enough data in frequency space to find a new Lorentzian, `widthExpansionRate` determines the rate at which the search area is expanded when trying to attain nearby data points. This is especially important when Lorentzians become very thin.

### Lorentz Fitting Factors

These all determine some aspect of either what the least squares fit converges over or the way in which the fit itself is conducted.

#### forceSingleLorentz

This disables multi-Lorentz fitting entirely. All Lorentzians will be treated as entirely their own entities. This could potentially cause a problem if Lorentzians overlap too closely.

#### multiFitLimit

Given a single Lorentzian, `multiFitLimit` times its full width half maximum determines the size of the area searched for creating a multi-Lorentzian fit.

#### peakSeparationFactor

This is a retired parameter used analagously to `multiFitLimit`. You do not need to change it.

#### terminationCostTolerance

The least squares fit needs to terminate under _some_ condition. Otherwise it will search forever. This sets the cost tolerance used in the termination. More will be added explaining the tolerance conditions and the choices used for the default conditions later.

#### terminationGradientTolerance

See `terminationCostTolerance`.

#### terminationIndependentTolerance

See `terminationIndependentTolerance`.

#### leastSquaresMethod

### Visualization Preferences

#### displayScale

#### liveUpdate

#### noiseFilterDisplay

#### peakPlotBackgroundColor

#### peakPlotFitColor

#### peakPlotPeakColor

### Detecting/Correcting Accidental Lorentz Degeneracies

#### closeLorentzAmplitude

#### closeLorentzFrequency

#### closeLorentzSkew

#### closeLorentzWidth

### Data Exports/Imports

#### allowedLogUpdates

#### dataExportHeaders

#### defaultExportDirectory

#### exportConfig

#### exportDataComplex

#### exportDataSimple

#### exportDirectory

#### exportFinalTrends

#### exportImages

#### exportParameters

#### exportVideo

### Pre-Detection Stuff

#### defaultImportDirectory

#### detectionTechnique

## Overview

TBD