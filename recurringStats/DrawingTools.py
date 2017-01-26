#!/usr/bin/python2

import PIL as pil
import math

from recurringStats.DT_ColorMaps import colorMaps

from PIL import ImageFont, ImageDraw

class colorScheme:
	def __init__(self):
		self.background = (200,200,200)
		self.noData 	= (255,255,255)
		self.error	 	= (  0,255,255)
		
		self.text       = (  0,  0,  0)
		self.line       = (  0,  0,  0)
	
		self.colors   = colorMaps.gradientMap
	
	def gradient(self,value):
		if math.isnan(value):
			return self.noData
		
		#if value > 10:
		#	return self.colors.tooLarge
		
		if self.colors[0][0] > value:
			return self.colors[0][1]

		for c in range(1, len(self.colors) ):
			if self.colors[c][0] > value:
				mix = float(self.colors[c][0]- value) / (self.colors[c][0]-self.colors[c-1][0])
				
				return tuple( [ int(self.colors[c][1][a] * (1-mix) + self.colors[c-1][1][a] * mix)
				                  for a in range(3) ] )

		#
		#  Didn't find a matching color
		#
		return self.colors[-1][1]
		
	

class cDrawingTool:
	def __init__(self):
		self.ticksLeft   = []
		self.ticksBottom = []
		self.title       = "NoName"
		
		self.pixelWidth  = 3
		self.pixelHeight = 10
		
		self.data        = []
		self.lines       =   7
		self.cols        = 288

		self.xlabel      = "xLabel"
		
		self.gradMin     = 20
		self.gradMax     = 35
		
		self.colors      = colorScheme()
		pass
		
	def initialize2(self,
						storageFolder,storageName,
						dayCount,entriesPerDay
						):
		self.setXLabel("Time of Day in hours")
		xTicks = []
		for h in range(25):
			xPos  = h*entriesPerDay/24
			xName = "{:d}".format(h)
			xTicks.append( [xPos, xName] )
		self.setTicksBottom(xTicks)
		
		self.setDataSize(lines=dayCount,cols=entriesPerDay)
		
		self.outFile = "{:s}/{:s}.png".format(storageFolder,storageName)
		
	def setMinMax(self, min, max):
		self.gradMin = float(min)
		self.gradMax = float(max)
		pass

	
	def setTitle(self, name):
		self.title = name
		pass

	def setXLabel(self, name):
		self.xlabel = name

	def setTicksBottom(self, names=[]):
		self.ticksBottom = names
		pass
	
	def setPixelSize(self,width=5,height=0):
		self.pixelWidth = width
		
		if height < 1:
			self.pixelHeight = width
		else:
			self.pixelHeight = height
		pass
	
	def setDataSize(self,lines=7,cols=288):
		self.lines = lines
		self.cols  = cols
		pass

	def dataLabelsIn(self, names=[]):
		self.ticksLeft = names
		pass
	
	def dataMatrixIn(self,data):
		self.data = data
		pass
	
	def draw(self, outFile=None):
		if outFile == None:
			outFile = self.outFile
		#
		#  Initialize...
		#  Fonts and stuff
		#
		font = pil.ImageFont.truetype( "fontfile.ttf", size=12 )
		fw_max, fh = font.getsize("0000-00-00")
		
		ySpace = 10
		xSpace = fw_max + 20
		
		#
		#  yTicks
		#
		yTicks = int( (fh+3) / self.pixelHeight + 1  )
		yTick  = int(self.lines-yTicks-1) % yTicks
		
		#
		#  Calculate required space
		#
		
		plotWidth   = self.pixelWidth  * self.cols
		plotHeight  = self.pixelHeight * self.lines
		
		imageWidth  = plotWidth  + 150 + fw_max 
		imageHeight = plotHeight +  80
		
		
		
		image  = pil.Image.new( "RGB", (imageWidth, imageHeight), self.colors.background )
		draw   = pil.ImageDraw.Draw(image)

		#
		#  Draw Title
		#
		tw, th = font.getsize( self.title )
		draw.text( ((imageWidth-tw)/2, ySpace), self.title, font=font, fill=self.colors.text)
		
		ySpace +=  th + 10
		
		#
		#  Draw Color Key
		#
		
		ck_x = xSpace+plotWidth+10
		ck_y = ySpace
		
		boxes = [
				["No data",     self.colors.noData ],
				#["No data",     self.colors.tooSmall ],
				#["Not reached", self.colors.tooLarge],
				["Wierd...",    self.colors.error],
			]

		keyHeight = plotHeight - len(boxes)*(12+2)

		draw.rectangle( [ck_x-1, ck_y-1, ck_x+11, ck_y+keyHeight+1], outline=self.colors.text )

		#gradient_min = self.colors[ 0][0] + self.gradShift
		#gradient_len = self.colors[-1][0] - gradient_min + self.gradShift

		for y in range(keyHeight+1):
			#value = gradient_min - self.gradShift + float(y)/keyHeight*gradient_len
			value = float(y)/keyHeight
			draw.line( [ck_x,     ck_y+keyHeight-y,
			  	    ck_x+10, ck_y+keyHeight-y], fill=self.colors.gradient(value)  )
			pass	
		for y in range(0,5):
			pos_x = ck_x + 15
			pos_y = int( ck_y + (1 - float(y)/4) * keyHeight)
			text  = "{:d}".format(int(self.gradMin + (self.gradMax-self.gradMin)*y/4))
			
			tw, th = font.getsize(text)
			draw.text( (pos_x+5, pos_y-th/2), text, fill=self.colors.text, font=font )
			
			draw.line( [pos_x-4, pos_y, pos_x, pos_y], fill=self.colors.text )

		boxcount = 0
		for box in boxes:
			box_y = ySpace + keyHeight + (12+2)*boxcount + 3

			draw.rectangle( [ck_x-1,    box_y, ck_x+11, box_y+12], fill=box[1], outline=self.colors.text )
			#draw.line(      [ck_x+12, box_y+5, ck_x+1, box_y+5], fill=self.colors.text )
			draw.text(      [ck_x+15, box_y], text=box[0], font=font, fill=self.colors.text )

			boxcount += 1

		
		#
		#  Draw Outline
		#
		draw.rectangle( [xSpace-1, ySpace-1, xSpace+plotWidth+1, ySpace+plotHeight+1], outline=self.colors.text )
		
		#
		#  Draw Lines
		#  1. Do we have a Name?
		for i in range(self.lines):
			if yTick == 0:
				yTick = yTicks
				
				yMid =  ySpace + self.pixelHeight/2
				
				draw.line( [xSpace, yMid, xSpace-3, yMid], fill=self.colors.text)
				
				tw, th = font.getsize( self.ticksLeft[i] )
				draw.text( (xSpace-tw-5, yMid-th/2), self.ticksLeft[i], fill=self.colors.text, font=font )
			#
			#  Draw Data
			#	
			for x in range(self.cols) :
				value = self.data[i][x]
				
				value -= self.gradMin
				value /= self.gradMax - self.gradMin
				if value < 0:
					value = 0

				x0 = xSpace+x*self.pixelWidth
				y0 = ySpace
				draw.rectangle( (x0,y0,x0+self.pixelWidth,y0+self.pixelHeight), fill=self.colors.gradient(value) )
			
			ySpace += self.pixelHeight
			yTick  -=  1
		
		for pos, name in self.ticksBottom:
			midx = int( xSpace+pos*self.pixelWidth )
			draw.line( [midx, ySpace, midx, ySpace+5], fill=self.colors.text)
			
			tw, th = font.getsize(name)
			draw.text( (midx-tw/2, ySpace+10), name, font=font, fill=self.colors.text)

		ySpace += 30
		#
		#  Draw XLabel
		#
		tw, th = font.getsize( self.xlabel )
		draw.text( ((imageWidth-tw)/2, ySpace), self.xlabel, font=font, fill=self.colors.text)
		
		ySpace +=  th + 15
		
		
		image.save(outFile, "PNG")
		pass
