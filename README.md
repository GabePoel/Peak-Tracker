# Current Status

There are _two_ semi-functional versions of the peak tracker at the moment. They are in the currentPeakTracker and modularPeakTracker directories. The retiredPeakTracker directory has a heavily modified version of the original peak tracker program that started getting so complex to work with that it had to be rewritten. Current Peak Tracker is a relatively feature rich, but somewhat buggy implementation based on a soft rewrite of the original peak tracker. It's what existed last week. Modular Peak Tracker on the other hand is a much more stable and easy to improve peak tracker, but it's currently incomplete and doesn't have the actual _tracking_ part peak tracking quite down yet. Modular Peak Tracker is a much harder rewrite of Current Peak Tracker that's designed to support the additional features we discussed last week. These include things like predicting the trajectory of peaks, allowing for a mutable number of peaks over the course of the tracking process, a more dynamic fitting procedure, and a more refined initial peak detection process. Of these, the peak detection process and the new fitting procedure (somewhat) can be seen. However, everything else is still a work in progress.

To run the Modular Peak Tracker, run the run.py file in the modularPeakTracker directory. And to run the Current Peak Tracker, run peakTracker.py in the currentPeakTracker directory. To play with the various features of these peak trackers and see what they currently do as well as a little bit of how they work, take a look at their respective modularConfig.py and config.py files. These allow you to play around with the different fitting and export parameters. If you want to see how your export is going as efficiently as possible, it's best to set exportVideo in config.py to True and liveUpdate to False. Then to see the overall fitting procedure, just watch the video in the associated export folder. Note that some image exports were pushed to GitHub, but the videos were too large. To make up for this, I've put some examples [here](https://drive.google.com/drive/folders/1C34p0-KxnbEElmJnfpiugvBKtVknyCEA?usp=sharing). I'd be happy to actually go through and explain every change, feature, and part of the peak trackers when possible.
