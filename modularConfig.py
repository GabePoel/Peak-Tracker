allowedLogUpdates = {"RATE_OF_CHANGE_PREDICTION": False, 
                     "AMPLITUDE_CORRECTION": True,
                     "SKEW_CORRECTION": True,
                     "WIDTH_CORRECTION": True,
                     "DEGENERACY_LOG": True,
                     "COST_LOG": False}
amplitudeGrowLimit = 3
amplitudeShrinkLimit = 3
backgroundSuppression = False
closeLorentzAmplitude = 1.2
closeLorentzFrequency = 1.2
closeLorentzSkew = 1.2
closeLorentzWidth = 1.2
curveFallBlocking = False
dataExportHeaders = True
defaultExportDirectory = "local" #"default", "local", or directory path
defaultImportDirectory = "default" #"default" or directory path
detectionTechnique = "manual" #"manual" or "automatic" (automatic doesn't work)
displayScale = "local" #"local" or "all"
displayTemp = False #don't use, doesn't work yet
enablePerturbations = True
exportConfig = True
exportDataComplex = True
exportDataSimple = True
exportDirectory = "default" #"default" or directory path
exportFinalTrends = True
exportImages = True
exportParameters = True
exportVideo = True
forceSingleLorentz = True
leastSquaresMethod = "dogbox"
liveUpdate = True
loadDirectory = "default" #"default" or directory path
multiFitLimit = 3
noiseFilterDisplay = True
noiseFilterLevel = 2
noiseFilterSmoothing = True
noiseFilterFlat = True
peakPlotBackgroundColor = 'b'
peakPlotFitColor = 'r'
peakPlotPeakColor = 'g'
rateOfChangeLength = 20
rateOfChangeTracking = True
reverseTrackingOrder = False
terminationCostTolerance = None
terminationGradientTolerance = None
terminationIndependentTolerance = 1e-15
trackingEndValue = "end" #"start", "end", or an integer index
trackingStartValue = 10 #"start", "end", or an integer index
widthExpansionBase = 2
widthExpansionRate = 1.1
widthGrowLimit = 1
widthShrinkLimit = 1.5
quickLoadDirectory = True #load directory from where you left off
quickLoadParameters = False #load parameters from where you left off
quickTracking = False
quickTrackingLength = 8