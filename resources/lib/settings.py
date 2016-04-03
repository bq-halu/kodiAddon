import sys
import xbmcaddon

__addon__      = sys.modules[ "__main__" ].__addon__

class settings():


	def __init__( self, *args, **kwargs ):

		self.readxml()
		self.addon = xbmcaddon.Addon()

	def readxml(self):
		self.haluIp             	= __addon__.getSetting("haluIp")
		self.idleLight				= int(int(__addon__.getSetting("idleLight").split(".")[0]))
		self.mode					= int(__addon__.getSetting("mode"))
		self.playRoom				= int(__addon__.getSetting("playRoom"))
		self.effectsIntensity		= int(int(__addon__.getSetting("effectsIntensity").split(".")[0]))
		self.enable					= __addon__.getSetting("enable") == "true"
		self.protocol				= int(__addon__.getSetting("protocol"))
		self.delay					= int(__addon__.getSetting("delay"))

	def update(self, **kwargs):
		self.__dict__.update(**kwargs)
		for k, v in kwargs.iteritems():
			self.addon.setSetting(k, v)

	def __repr__(self):
		return 'Enable: %s,  ' % str(self.enable) + 'haluIp: %s\n ' % self.haluIp + \
		'Idle intensity: %s\n' % str(self.idleLight) + \
		'mode (0=fullscreen, 1=rightUpLeft) :%s\n' % str(self.mode) + 'Room %s, ' % str(self.playRoom) + \
		'Effects intensity: %s\n' % str(self.effectsIntensity) + \
		'Protocol (0=TCP, 1=UDP): %s, ' % str(self.protocol) + \
		'Delay: %s' % str(self.delay) 