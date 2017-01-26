import datetime
import math
import os


class eStatsPolicy:
	average  = 1
	lowest   = 2
	highest  = 3

class cDailyData:
	def __init__(self, date, entriesPerDay, storageFile, storagePolicy):
		self.date             = date
		self.entriesPerDay    = entriesPerDay
		self.storageFile      = storageFile
		self.storagePolicy    = storagePolicy
	
		self.dataPoints       = [ [0 , 0] for i in range(entriesPerDay) ]
		
		self.readFromFile()
	
	def __del__(self):
		pass
		#self.storeInFile()
		
	def getDate(self):
		return self.date
	
	def insert(self, value, time):
		slot = int( self.entriesPerDay * (time.hour * 60 + time.minute) / (24*60) )
		
		#force conversion to float.
		value = float(value)
		
		if self.storagePolicy == eStatsPolicy.lowest:
			if 0 == self.dataPoints[slot][1]:
				self.dataPoints[slot][0] = value
				self.dataPoints[slot][1] = 1
			else:
				if self.dataPoints[slot][0] > value:
					self.dataPoints[slot][0] = value
					
		elif self.storagePolicy == eStatsPolicy.highest:
			if 0 == self.dataPoints[slot][1]:
				self.dataPoints[slot][0] = value
				self.dataPoints[slot][1] = 1
			else:
				if self.dataPoints[slot][0] < value:
					self.dataPoints[slot][0] = value
					
		elif self.storagePolicy == eStatsPolicy.average:
			self.dataPoints[slot][0] += (value-self.dataPoints[slot][0]) / (self.dataPoints[slot][1] + 1)
			self.dataPoints[slot][1] += 1
		else:
			print("DEBUG::Statspolicy failed")
		pass
		
	def storeInFile(self):
		with open( self.storageFile, "w") as outData:		
			for slot in range(self.entriesPerDay):
				line = self.dataPoints[slot]
				outData.write("{value:f}\t{count:d}\n".format( value=line[0], count=line[1] ) )
		pass

	def readFromFile(self):
		try:
			inData = open( self.storageFile ).readlines()
		except FileNotFoundError:
			#print("Read failed for {:s} FileNotFound".format(self.storageFile) )
			return

		lineCounter = 0
		for line in inData:
			lineData = line.split("\t")
			self.dataPoints[lineCounter] = [ float(lineData[0]) , int(lineData[1]) ]
			lineCounter += 1
			
		pass
	
	def getMatrixLine(self):
		line = []
		for p in self.dataPoints:
			if p[1] == 0:
				line.append(float('nan'))
			else:
				line.append( p[0] )
		return line
		
	
class cStatisticsManagement:

	def __init__(self, storageFolder, storagePrefix, dayCount, entriesPerDay, policy=eStatsPolicy.average ):
		#
		#  declare fixed class variables
		#
		self.storageFolder     = storageFolder
		os.makedirs(storageFolder, exist_ok=True) #ensure the directories exist
		self.storageFilePrefix = storagePrefix
		self.storageFileFormat = "{folder:s}/{prefix:s}_{year:04d}-{month:02d}-{day:02d}.dat"

		self.dayCount      = dayCount
		self.entriesPerDay = entriesPerDay
		#
		#  declare changing class variables
		#
		self.data=[]
		
		for i in range(dayCount):
			runner = datetime.date.today() - datetime.timedelta(days=i)

			dayData = cDailyData(
							date=runner,
							entriesPerDay=entriesPerDay, 
							storageFile=self.storageFileFormat.format(
								folder=self.storageFolder,
								prefix=self.storageFilePrefix,
								year=runner.year,
								month=runner.month,
								day=runner.day,
								), 
							storagePolicy=eStatsPolicy.average,
							)
			self.data.append(dayData)
		return
		
	def getData(self):
		return self.data
		
	def addValueAsNow(self,value):
		now = datetime.datetime.now()
		today = now.date()
		
		if today != self.data[0].getDate():
			#
			#  Store currend data when replacing
			#
			self.data[0].storeInFile() 
			del self.data[-1]
			dayData = cDailyData(
							date=today,
							entriesPerDay=self.entriesPerDay, 
							storageFile=self.storageFileFormat.format(
								folder=self.storageFolder,
								prefix=self.storageFilePrefix,
								year=today.year,
								month=today.month,
								day=today.day,
								), 
							storagePolicy=eStatsPolicy.average,
							)
			self.data = [dayData] + self.data
		
		self.data[0].insert(value, now)
		
		#DEBUG (not needed every time)
		self.data[0].storeInFile()
		
		return
		
		
