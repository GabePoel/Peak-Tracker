import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

class ModularVisualizer:
    def __init__(self, parent, master=None):
        self.fig = parent.fig
        self.ax = parent.ax
        self.parent = parent
        self.root = tk.Tk()
        self.root.wm_title("Live Peak Tracker Visualizer")
        self.controls = tk.Frame(self.root)
        self.controls.pack(side="top", fill="both", expand=True)
        detectButton = tk.Button(master=self.root, text="Detect Peaks", \
            command=self.detectPeaks)
        loadButton = tk.Button(master=self.root, text="Load Data", \
            command=self.loadDataSet)
        importButton = tk.Button(master=self.root, text="Set Import", \
            command=self.setImportDirectory)
        exportButton = tk.Button(master=self.root, text="Set Export", \
            command=self.setExportDirectory)
        closeButton = tk.Button(master=self.root, text="Close Window", \
            command=self.closeWindow)
        restartButton = tk.Button(master=self.root, text="Restart Program", \
            command=self.restartProgram)
        backgroundButton = tk.Button(master=self.root, text="See Background", \
            command=self.displayBackground)
        quickButton = tk.Button(master=self.root, text="Quick Display", \
            command=self.fullPreviewDisplay)
        saveButton = tk.Button(master=self.root, text="Save Current Peaks", \
            command=self.saveParameters)
        parameterButton = tk.Button(master=self.root, text="Load New Peaks", \
            command=self.loadParameters)
        detectButton.pack(in_=self.controls, side="left")
        loadButton.pack(in_=self.controls, side="left")
        importButton.pack(in_=self.controls, side="left")
        exportButton.pack(in_=self.controls, side="left")
        closeButton.pack(in_=self.controls, side="left")
        restartButton.pack(in_=self.controls, side="left")
        backgroundButton.pack(in_=self.controls, side="left")
        quickButton.pack(in_=self.controls, side="left")
        saveButton.pack(in_=self.controls, side="left")
        parameterButton.pack(in_=self.controls, side="left")
        self.prepWindow()
        self.runWindow()

    def fullPreviewDisplay(self):
        self.parent.quickDisplay()

    def prepWindow(self):
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.parent.canvas = self.canvas
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="bottom", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        self.toolbar.update()
        self.canvas._tkcanvas.pack()

    def displayBackground(self):
        self.parent.circlePreview()

    def closeWindow(self):
        self.root.quit()
        self.root.destroy()

    def updateWindow(self):
        self.canvas._tkcanvas.pack_forget()
        self.toolbar.pack_forget()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="bottom", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        self.toolbar.update()
        self.canvas._tkcanvas.pack()

    def runWindow(self):
        tk.mainloop()

    def restartProgram(self):
        self.closeWindow()
        import modularRestart
        modularRestart.restart()

    def saveParameters(self):
        self.parent.saveCurrentParameters()

    def loadParameters(self):
        self.parent.loadSavedParameters()

    def loadDataSet(self):
        self.ax.cla()
        self.parent.loadDataSet()

    def setImportDirectory(self):
        tk.Tk().withdraw()
        self.parent.setImportDirectory(tk.filedialog.askdirectory())

    def setExportDirectory(self):
        tk.Tk().withdraw()
        self.parent.setExportDirectory(tk.filedialog.askdirectory())

    def detectPeaks(self):
        self.parent.detectPeaks()
