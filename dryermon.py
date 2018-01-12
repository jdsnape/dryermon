import paho.mqtt.client as mqtt
import datetime
import time
import json


class State(object):
    """
    We define a state object which provides some utility functions for the
    individual states within the state machine.
    """
    def __init__(self):
        print 'Processing current state:', str(self)
	self.threshold = 100
	self.end_delay = 300 #time to wait before confirming we're done in seconds	
	self.timer = 0

    def on_event(self, event):
        """
        Handle events that are delegated to this State.
        """
        pass

    def __repr__(self):
        """
        Leverages the __str__ method to describe the State.
        """
        return self.__str__()

    def __str__(self):
        """
        Returns the name of the State.
        """
        return self.__class__.__name__


class idle(State):
	def on_event(self, event):
		if event > self.threshold:
			return running()

class running(State):
	def on_event(self, event):
		print(event)
		if event < self.threshold:
			return maybe_finished()
		else:
			return running()
	
class maybe_finished(State):
	def on_event(self, event):
		print("We think we may be finished, but want to wait a while")
		#If the power's gone back up then we're not finished
		if event > self.threshold:
			return running()
		else:
			if self.timer == 0:
				self.timer = time.time()
			elif (time.time() - self.end_delay) > self.timer:
				return idle()
			else:
				return maybe_finished()


class dryer(object):
	def __init__(self):
		self.state = idle()

	def on_event(self, event):
		self.state = self.state.on_event(event)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("myhome/garage/dryer/tele/SENSOR")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(str(msg.payload))
    dryer.on_event(json.loads(msg.payload)["ENERGY"]["Power"])


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("127.0.0.1", 1883, 60)

dryer = dryer()
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
