import xbmc
import xbmcgui
import xbmcaddon
import json
import time
import sys
import colorsys
import os
import datetime
import math
#import netifaces
import urllib2
from threading import Thread
import socket
import collections


__addon__      = xbmcaddon.Addon()
__addonS__      = sys.modules[ "__main__" ].__addon__

__cwd__        = __addon__.getAddonInfo('path')
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )


sys.path.append (__resource__)

from settings import *
from tools import *

try:
  import requests
except ImportError:
  xbmc.log("ERROR: Could not locate required library requests")
  notify("XBMC Halu", "ERROR: Could not import Python requests")

xbmc.log("XBMC Halu service started, version: %s" % get_version())





portDiscovery = 1900  # Udp discovery port
UDP_PORT = 2345
UDP_IP = '10.255.255.255'
localPort = 50123

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


player = None
capture = xbmc.RenderCapture()

fmt = capture.getImageFormat()
# BGRA or RGBA
# xbmc.log("Hue Capture Image format: %s" % fmt)
fmtRGBA = fmt == 'RGBA'

#rgbw = [[0 for x in xrange(3)] for x in xrange(4)]
rgbw = [[0,0,0,0],[0,0,0,0],[0,0,0,0]]
maximo = 0

factorR = float( 255.0 / 200.0 )
factorV = float( 255.0 / 81.0 )
factorA = float( 255.0 / 237.0 )
factorB = float( 255.0 / 36.0 )





class MyMonitor( xbmc.Monitor ):
	def __init__( self, *args, **kwargs ):
		xbmc.Monitor.__init__( self )

	def onSettingsChanged( self ):
		last = datetime.datetime.now()
		h.updateDB()
monitor = MyMonitor()

logger = Logger()

try:
	import requests
except ImportError:
	logger.log("ERROR: Could not locate required library requests")
	notify("Kodi Halu", "ERROR: Could not import Python requests")



waitTime = time.time()



logger.log("Kodi Halu, version: %s" % get_version())






def rpiColor(r,g,b):

	bl = min(r, g, b)	#white component
	
	rc = r - bl 			#pure color component
	gc = g - bl
	bc = b - bl

	bl = bl * factorB
	r = rc * factorR
	g = gc * factorV
	b = bc * factorA

	return int(r + bl), int(g + bl), int(b + bl) 






class MyPlayer(xbmc.Player):
	duration = 0


	def __init__(self):
		xbmc.Player.__init__(self)
	
	def onPlayBackStarted(self):
		if self.isPlayingVideo():
			logger.log("Video starts")
			qqthreadCapture.playingVideo = True
			qqthreadCapture.playingAudio = False
		if self.isPlayingAudio():
			logger.log("Audio starts")
			qqthreadCapture.playingVideo = False
			qqthreadCapture.playingAudio = True
			#logger.log(self.getAvailableAudioStreams())

	def onPlayBackPaused(self):

		if self.isPlayingVideo():
			logger.log("Video paused")
		if self.isPlayingAudio():
			logger.log("Audio paused")
		qqthreadCapture.playingVideo = False
		qqthreadCapture.playingAudio = False
		h.qq_postSpaceColor()

	def onPlayBackResumed(self):
		if self.isPlayingVideo():
			logger.log("Video reumed")
			qqthreadCapture.playingVideo = True
			qqthreadCapture.playingAudio = False
		if self.isPlayingAudio():
			logger.log("Audio resumed")
			qqthreadCapture.playingVideo = False
			qqthreadCapture.playingAudio = True

	def onPlayBackStopped(self):
		if self.isPlayingVideo():
			logger.log("Video stoped")
		if self.isPlayingAudio():
			logger.log("Audio stoped")
		qqthreadCapture.playingVideo = False
		qqthreadCapture.playingAudio = False
		h.qq_postSpaceColor()

	def onPlayBackEnded(self):
		if self.isPlayingVideo():
			logger.log("Video ended")
		if self.isPlayingAudio():
			logger.log("Audio ended")
		qqthreadCapture.playingVideo = False
		qqthreadCapture.playingAudio = False
		h.qq_postSpaceColor()


def getAvgColor():
	global maximo

	r, g, b, w = 0, 0, 0, 0

	for x in range(3):
		for y in range(4):
			rgbw[x][y] = 0


	if qqthreadCapture.playingVideo and (h.connected == True):
		capture_width = 32 #100
		capture_height = int(capture_width / capture.getAspectRatio())

		wFifth = int(capture_width / 5)
		hFifth = int(capture_height / 5)
		hThird = int(capture_height / 3)

		capture.capture(capture_width, capture_height, xbmc.CAPTURE_FLAG_CONTINUOUS)
		#capture.capture(capture_width, capture_height)
		#capture.capture()
		
		espera = time.time()
		while capture.getCaptureState() != xbmc.CAPTURE_STATE_DONE:
			if not(qqthreadCapture.playingVideo):
				logger.log("Not playing > do not capture!")
				return
			#time.sleep(0.001)
			if (time.time() - espera) > 8:
				logger.log("estado:" + str(capture.getCaptureState()) + "done:" + str(xbmc.CAPTURE_STATE_DONE) + "working:" + str(xbmc.CAPTURE_STATE_WORKING) + "Failed:" + str(xbmc.CAPTURE_STATE_FAILED))
				capture.capture(capture_width, capture_height, xbmc.CAPTURE_FLAG_CONTINUOUS)  
				logger.log("long waiting for capture done, asking again")
				espera = time.time()
		espera = time.time() - espera

		#logger.log("TIEMPO Espera: " + str(espera))

		pix = time.time()
		if qqthreadCapture.playingVideo: 
			pixels = capture.getImage()
		else:
			return
		pix = time.time() - pix

		p = 0
		size = int(len(pixels)/4)
		z1 = 0	#pixel counter for left area
		z2 = 0	# 				"					center up
		z3 = 0	# 				"					right

		if h.settings.mode == 0:	#one zone mode, full screen
			
			for i in range(size):
				if fmtRGBA:
					r += pixels[p]
					g += pixels[p + 1]
					b += pixels[p + 2]
				else: #probably BGRA
					b += pixels[p]
					g += pixels[p + 1]
					r += pixels[p + 2]
				p += 4
			rgbw[0][0] = r / size
			rgbw[0][1] = g / size
			rgbw[0][2] = b / size
			if h.settings.rpi:
				rgbw[0][0], rgbw[0][1], rgbw[0][2] = rpiColor(rgbw[0][0], rgbw[0][1], rgbw[0][2])

			rgbw[0][3] = min(rgbw[0][0], rgbw[0][1], rgbw[0][2]) / 4
			#logger.log("RGB["+ str(r) + ',' + str(g) + ',' + str(b) + '], rgbw[0]='+ str(rgbw[0]) + 'size: ' + str(size) )

		else:
			#logger.log("capture format: " + fmt)
			for i in range(size):
				if fmtRGBA:
					r = pixels[p]
					g = pixels[p + 1]
					b = pixels[p + 2]
				else: #probably BGRA
					b = pixels[p]
					g = pixels[p + 1]
					r = pixels[p + 2]
				#logger.log('p[' + str(pixels[p]) + ',' + str(pixels[p+1]) + ',' + str(pixels[p+2]) + ',' + str(pixels[p+3]) +']')
				p += 4

				cx = i % capture_width
				cy = i / capture_width
				
				if (cx < wFifth):
					if (cx > cy):
						z2 += 1
						rgbw[1][0] += r
						rgbw[1][1] += g 	#center up
						rgbw[1][2] += b
					else:
						z1 += 1
						rgbw[0][0] += r
						rgbw[0][1] += g 	#left
						rgbw[0][2] += b
				elif (cx < (capture_width - wFifth)):
					if (cy < hThird):
						z2 += 1
						rgbw[1][0] += r
						rgbw[1][1] += g 	#center up
						rgbw[1][2] += b
				elif (cy < hFifth):
					if (cx - (capture_width - wFifth)) > cy :
						z2 += 1
						rgbw[1][0] += r
						rgbw[1][1] += g 	#center up
						rgbw[1][2] += b
				else:
					z3 += 1
					rgbw[2][0] += r
					rgbw[2][1] += g 	#right
					rgbw[2][2] += b
			
			#logger.log("rgbw="+ str(rgbw))		
			if h.settings.rpi:
				rgbw[0][0], rgbw[0][1], rgbw[0][2] = rpiColor(rgbw[0][0], rgbw[0][1], rgbw[0][2])
				rgbw[1][0], rgbw[1][1], rgbw[1][2] = rpiColor(rgbw[1][0], rgbw[1][1], rgbw[1][2])
				rgbw[2][0], rgbw[2][1], rgbw[2][2] = rpiColor(rgbw[2][0], rgbw[2][1], rgbw[2][2])
			#logger.log("RPIrgbw="+ str(rgbw))
			rgbw[0][0] = rgbw[0][0] / z1
			rgbw[0][1] = rgbw[0][1] / z1
			rgbw[0][2] = rgbw[0][2] / z1


			rgbw[0][3] = min(rgbw[0][0], rgbw[0][1], rgbw[0][2]) / 4

			rgbw[1][0] = rgbw[1][0] / z2
			rgbw[1][1] = rgbw[1][1] / z2
			rgbw[1][2] = rgbw[1][2] / z2
			rgbw[1][3] = min(rgbw[1][0], rgbw[1][1], rgbw[1][2]) / 4

			rgbw[2][0] = rgbw[2][0] / z3
			rgbw[2][1] = rgbw[2][1] / z3
			rgbw[2][2] = rgbw[2][2] / z3
			rgbw[2][3] = min(rgbw[2][0], rgbw[2][1], rgbw[2][2]) / 4

			#logger.log("End values: " + str(rgbw))

		#logger.log(rgbw[0])

	return 



class Halu:

	connected = False
	database = {}
	lamp_db = []
	left = []
	right = []
	centerUp = []
	#timeFromPlay = time.time()
	

	def __init__(self, settings):
		#self.discovery()

		self.settings = settings
		self.connected = False
		self.system = None

		self.updateDB()
		if self.connected:
			self.qq_postSpaceColor()
			
		


	def updateDB(self):
		
		database = {}
		self.settings.readxml()
		if self.settings.enable:
			logger.log("settings.xml loaded,\n       %s" % self.settings)
			if self.getDatabase():
				self.connected = True
				self.loadLamps()			
			else:
				self.connected = False
		else:
			logger.log(" Halu disbabled from settings!")


	def loadLamps(self):
		
		self.left[:] = []
		self.right[:] = []
		self.centerUp[:] = []

		logger.log("num lamps: %s" % str(len(self.lamp_db)))
		for i in range(len(self.lamp_db)):
			if (self.database["data"]["lamp_db"][i]["available"] == True) and (self.database["data"]["lamp_db"][i]["space_id"] == self.settings.playRoom):#space_id for reproductor
				if self.database["data"]["lamp_db"][i]["position"]["x"] < 0:
					self.left.append(self.database["data"]["lamp_db"][i]['id'])
				elif self.database["data"]["lamp_db"][i]["position"]["x"] >0:
					self.right.append(self.database["data"]["lamp_db"][i]['id'])
				elif (self.database["data"]["lamp_db"][i]["position"]["x"] == 0) and (self.database["data"]["lamp_db"][i]["position"]["z"] >0 ):
					self.centerUp.append(self.database["data"]["lamp_db"][i]['id'])

		logger.log("Left Lamps ID's: %s" % str(self.left))
		logger.log("right Lamps ID's: %s" % str(self.right))
		logger.log("centerUp Lamps ID's: %s" % str(self.centerUp))		



	def discovery(self):
		#Thanks Nick Riviera!

		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.setblocking(0)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		s.bind(('', localPort))

		for interfaz in netifaces.interfaces() :
			#logger.log(interfaz)
			addrs = netifaces.ifaddresses(interfaz)
			try :
				data =	addrs[netifaces.AF_INET]
				#logger.log(data)
			except:
				#logger.log("no valid IPv4.")
				continue

			for i, d in enumerate([e for e in data if "broadcast" in e.keys()]):

				#logger.log("intentando con:" + d["broadcast"])
				try:
					s.sendto("qq_discovery", (d["broadcast"], portDiscovery))
				except Exception as error:
					#logger.log("error: %s" % error)
					break
				start = time.time()
				while time.time() - start < 2 :
					try:
						llega, address = s.recvfrom(4096)
					except:
						s.sendto("qq_discovery", (d["broadcast"], portDiscovery))
						time.sleep(0.05)
						continue
					try:
						jllega = json.loads(llega)
						ipInt = jllega["data"]["access_point_db"]["ip"]
						ipExt = jllega["data"]["connection_db"]["ip"]

					except Exception as error:
						#logger.log("No es Halu!! %s" % error)
						continue
					logger.log("Halu encontrada!!")
					self.connected = True
					self.settings.haluIp = address[0]
					return self.connected
		return 'None'



	def getDatabase(self):
		urlLamp = 'http://' + str(self.settings.haluIp) + ':2015/master/database'
		try:
			req = requests.get(urlLamp)
		except:
			logger.log("Halu not found")

			return False

		#logger.log(req.status_code)
		#logger.log(req.headers)
		#logger.log(req.content)
		try:
			self.database = json.loads(req.content)
		except Exception as error:
			logger.log("Error getting the Json database: %s" % str(error))
			return False
		self.lamp_db[:] = []
		self.lamp_db = self.database["data"]["lamp_db"]
		#logger.log(lamp_db)
		#logger.log("constants.SYSTEM: " + constants.SYSTEM)
		logger.log("sys.platform: " + sys.platform)


		return True



	def qq_postEffect(self):
		urlEffect = 'http://' + str(self.settings.haluIp) + ':2015/master/effect'

		data = {'duration': 1, 'priority': 1, 'steps': []}

		j = float(self.settings.effectsIntensity)/100

		if self.settings.mode ==0:
			data["steps"].append({'color' : {'components': {'r': rgbw[0][0], 'g': rgbw[0][1], 'b': rgbw[0][2], 'w': rgbw[0][3]}, 'fade' : 0.07, 'intensity' : j},'target': {'id': self.settings.playRoom, 'type': 'space'}, 'start_time': 0})
		else:

			for i in range(len(h.left)):
				data["steps"].append({'color' : {'components': {'r': rgbw[0][0], 'g': rgbw[0][1], 'b': rgbw[0][2], 'w': rgbw[0][3]}, 'fade' : 0.07, 'intensity' : j},'target': {'id': h.left[i], 'type': 'lamp'}, 'start_time': 0})
			for i in range(len(h.centerUp)):
				data["steps"].append({'color' : {'components': {'r': rgbw[1][0], 'g': rgbw[1][1], 'b': rgbw[1][2], 'w': rgbw[1][3]}, 'fade' : 0.07, 'intensity' : j},'target': {'id': h.centerUp[i], 'type': 'lamp'}, 'start_time': 0})
			for i in range(len(h.right)):
				data["steps"].append({'color' : {'components': {'r': rgbw[2][0], 'g': rgbw[2][1], 'b': rgbw[2][2], 'w': rgbw[2][3]}, 'fade' : 0.07, 'intensity' : j},'target': {'id': h.right[i], 'type': 'lamp'}, 'start_time': 0})

		#logger.log(urlEffect)
		#logger.log(data)
		req = urllib2.Request(urlEffect)
		req.add_header('Content-Type', 'application/json')
		#response = urllib2.urlopen(req, json.dumps(data))
		#logger.log(urlEffect)
		#logger.log(data)
		#logger.log(response)
		if qqthreadCapture.playingVideo: 
			try:
				response = urllib2.urlopen(req, json.dumps(data))	
			except Exception as error:
				logger.log("fail on POST: %s" % str(error))
				logger.log("url: %s" % urlEffect)
				logger.log("data: %s" % data)
		
		return



	def qq_sendUDP(self):
		#data = collections.OrderedDict((( "method" , "POST"), ("target" , "lamp"), ("action", "effect"), ("data", { 'steps': [] })))

		data = {"method": "POST", "target" : "lamp", "action": "effect", 'data':{'duration': 1, 'priority': 1, 'steps': []}}

		j = float(self.settings.effectsIntensity)/100

		if self.settings.mode ==0:
			data["data"]["steps"].append({'color' : {'components': {'r': rgbw[0][0], 'g': rgbw[0][1], 'b': rgbw[0][2], 'w': rgbw[0][3]}, 'fade' : 0.07, 'intensity' : j},'target': {'id': self.settings.playRoom, 'type': 'spaceUdp'}, 'start_time': 0})
		else:

			for i in range(len(h.left)):
				data["data"]["steps"].append({'color' : {'components': {'r': rgbw[0][0], 'g': rgbw[0][1], 'b': rgbw[0][2], 'w': rgbw[0][3]}, 'fade' : 0.07, 'intensity' : j},'target': {'id': h.left[i], 'type': 'lampUdp'}, 'start_time': 0})
			for i in range(len(h.centerUp)):
				data["data"]["steps"].append({'color' : {'components': {'r': rgbw[1][0], 'g': rgbw[1][1], 'b': rgbw[1][2], 'w': rgbw[1][3]}, 'fade' : 0.07, 'intensity' : j},'target': {'id': h.centerUp[i], 'type': 'lampUdp'}, 'start_time': 0})
			for i in range(len(h.right)):
				data["data"]["steps"].append({'color' : {'components': {'r': rgbw[2][0], 'g': rgbw[2][1], 'b': rgbw[2][2], 'w': rgbw[2][3]}, 'fade' : 0.07, 'intensity' : j},'target': {'id': h.right[i], 'type': 'lampUdp'}, 'start_time': 0})
		if qqthreadCapture.playingVideo: 
			try: 
				sock.sendto(json.dumps(data), (UDP_IP, UDP_PORT))
			except Exception as error:
				logger.log("fail sending udp effect, reason: %s" % str(error))


	def qq_postSpaceColor(self):

		if self.settings.enable:
		
			logger.log("sending space commad for idle state.")
			urlEffect = 'http://' + str(self.settings.haluIp) + ':2015/space/' + str(self.settings.playRoom) + '/color'
			

			data = {'components': {'r': 255, 'g': 255, 'b': 150, 'w': 255}, 'fade' : 1, 'intensity' : float(self.settings.idleLight)/100}

			req = urllib2.Request(urlEffect)
			req.add_header('Content-Type', 'application/json')

			try:
				response = urllib2.urlopen(req, json.dumps(data))	
			except Exception as error:
				logger.log("fail on POST: %s" % str(error))
				logger.log("url: %s" % urlEffect)
				logger.log("data: %s" % data)
		else:
			logger.log("No space order sent because Halu is disbabled.")
		return






class loop(Thread):

	def __init__(self):
		''' Constructor. '''
		Thread.__init__(self)
		self.playingVideo = False
		self.playingAudio = False

		self.exit = False

	def run(self):
		global waitTime
		global img
		method = 'None'

		while not(self.exit) :
			waitTime = time.time() - waitTime
			if (h.connected == True) and h.settings.enable :
				colorTime = time.time()
				getAvgColor()
				colorTime = time.time() -colorTime

				sendTime = time.time()
				if self.playingVideo:
					if h.settings.protocol == 0 :	#0 = TCP, 1 = UDP
						h.qq_postEffect()
						method ='tcp'
					else :	
						h.qq_sendUDP()
						method = 'udp'
					sendTime = time.time() - sendTime
					seconds = waitTime + colorTime + sendTime 
					logger.log(method + "FPS:{0}".format(1/seconds) + " waitTime:" + str(waitTime) + " ColorTime:" + str(colorTime) + " PostTime:" + str(sendTime))
				
			elif self.playingAudio and (h.connected == True):
				logger.log("audio playing")
				xbmc.sleep(2000)
			else:
				xbmc.sleep(2000)
			waitTime = time.time()
			xbmc.sleep(h.settings.delay)





logger.log("Halu init!!")

sett = settings()


h = Halu(sett)
qqthreadCapture = loop()


if ( __name__ == "__main__" ):
	qqthreadCapture.start()
	last = datetime.datetime.now()
	while not xbmc.abortRequested:

		if player == None:
			
			player = MyPlayer()
		xbmc.sleep(100)

	logger.log("exiting capture thread")
	qqthreadCapture.exit = True
	xbmc.sleep(200)
	qqthreadCapture.join()
