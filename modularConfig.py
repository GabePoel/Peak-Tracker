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
defaultExportDirectory = "local" #"default", "local", or directory path
defaultImportDirectory = "default" #"default" or directory path
detectionTechnique = "manual" #"manual" or "automatic" (automatic doesn't work)
displayScale = "local" #"local" or "all"
displayTemp = False #don't use, doesn't work yet
enablePerturbations = True
exportConfig = True
exportDataComplex = False
exportDataSimple = True
exportDirectory = "default" #"default" or directory path
exportFinalTrends = True
exportImages = True
exportParameters = True
exportVideo = True
forceSingleLorentz = False
leastSquaresMethod = "dogbox"
liveUpdate = True
loadDirectory = "default" #"default" or directory path
multiFitLimit = 2
noiseFilterDisplay = True
noiseFilterLevel = 4
noiseFilterSmoothing = True
noiseFilterFlat = True
peakSeparationFactor = 50
peakPlotBackgroundColor = 'b'
peakPlotFitColor = 'r'
peakPlotPeakColor = 'g'
rateOfChangeLength = 50
rateOfChangeTracking = False
reverseTrackingOrder = False
terminationCostTolerance = None
terminationGradientTolerance = None
terminationIndependentTolerance = 1e-15
trackingEndValue = "end" #"start", "end", or an integer index
trackingStartValue = 10 #"start", "end", or an integer index
widthExpansionBase = 3
widthExpansionRate = 1
widthGrowLimit = 1
widthShrinkLimit = 1
quickLoadDirectory = True #load directory from where you left off
quickLoadParameters = False #load parameters from where you left off
quickTracking = False
quickTrackingLength = 5