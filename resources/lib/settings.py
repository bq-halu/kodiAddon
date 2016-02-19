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

	def update(self, **kwargs):
		self.__dict__.update(**kwargs)
		for k, v in kwargs.iteritems():
			self.addon.setSetting(k, v)

	def __repr__(self):
		return 'haluIp: %s\n' % self.haluIp + \
		'Idle intensity: %s\n' % str(self.idleLight) + \
		'mode %s\n' % str(self.mode) + 'Room %s\n' % str(self.playRoom) + \
		'Effects intensity: %s ' % str(self.effectsIntensity)