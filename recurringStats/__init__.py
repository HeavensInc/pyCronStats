import recurringStats.StatisticsManagement as StatisticsManagement
import recurringStats.DrawingTools as DrawingTools
import subprocess # for safe PING


class eJobType:
	none       = 0
	fileRead   = 1
	pingHost   = 2

class cRecurringStats:
	def __init__(self,storageFolder,storageName,dayCount,entriesPerDay):
		self.stats = StatisticsManagement.cStatisticsManagement(
							storageFolder=storageFolder,
							storagePrefix=storageName,
							dayCount=dayCount,
							entriesPerDay=entriesPerDay
						)
		self.draw = DrawingTools.cDrawingTool()
		self.draw.initialize2(storageFolder,storageName,dayCount,entriesPerDay)
		
		self.jobType  = eJobType.none
		self.jobArgs  = ""
		self.prepared = False

	def setupAsFileRead(self, filename, titleOverride=None, range=[10, 30],):
		if not self.prepared:
			self.jobType  = eJobType.fileRead
			self.jobArgs  = filename
			self.prepared = True
			
			if None == titleOverride:
				self.draw.setTitle("Fileread from: {:s}".format(filename) )
			else:
				self.draw.setTitle(titleOverride)
			self.draw.setMinMax(range[0],range[1])
			
		else:
			#progress alreadyPrepared
			pass
		
	def setupAsPingHost(self, host, titleOverride=None, range=[0,100]):
		if not self.prepared:
			self.jobType  = eJobType.pingHost
			self.jobArgs  = host
			self.prepared = True
			
			if None == titleOverride:
				self.draw.setTitle("Fileread from: {:s}".format(filename) )
			else:
				self.draw.setTitle(titleOverride)
			self.draw.setMinMax(range[0],range[1])
		else:
			#progress alreadyPrepared
			pass
			
	def executeGathering(self):
		if self.jobType == eJobType.fileRead:
			value = float( open(self.jobArgs).read() )
			self.stats.addValueAsNow(value)
			
		elif self.jobType == eJobType.pingHost:
			try:
				ping_response = subprocess.Popen(["/bin/ping", "-c4", "-q", self.jobArgs], stdout=subprocess.PIPE).stdout.readlines()
				ping          = ping_response[-1]
				ping          = str(ping).split("/")
				ping          = ping[4]
				ping          = float( ping )
			except IndexError:
				ping          = 10000.0
			except TypeError:
				ping          = 10000.0
			self.stats.addValueAsNow(ping)
		else:
			#progress noJobError?
			pass
		
	def executeDrawing(self):
		labels = []
		matrix = []
		
		for k in self.stats.getData():
			labels.append(k.date.isoformat())
			matrix.append(k.getMatrixLine())
		
		labels[0] = "Today"	
		#
		#  item ::-1 means reversed
		#
		self.draw.dataLabelsIn(labels[::-1])
		self.draw.dataMatrixIn(matrix[::-1])
		self.draw.draw()
	
		
