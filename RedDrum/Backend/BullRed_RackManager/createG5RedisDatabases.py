import redis
import json
from .redisTransport import RedisTransport


class RedisDb(object):
	"""RedisDb"""
	def __init__(self, ip, port=6379,decode=True):
		self.rdt = RedisTransport(ip, port=6379,decode=True)

	# Initiating redis-Python connection.
	# Redis connection pool is shared across multiple threads.
	# It is not safe to close them. Python garbage collector disconnects it after the 
	# redis connection goes out of scope. It is smart that way. 
	def init_connect(self):
		conn = self.rdt.connect()
		if conn is not None:
			return (conn)

	#Creating a non-empty hashes in redis
	def constructHashes(self,conn):
		val = {'key1' : 'value1'}
		json_val = json.dumps(val)
		try:
			status,msg = self.rdt.setHashDbEntry("ChassisMonHashDb",'chassisId',val)
			status,msg = self.rdt.setHashDbEntry("ManagersMonHashDb",'managerId',val)
			status,msg = self.rdt.setHashDbEntry("SystemsMonHashDb",'systemsId',val)
			status,msg = self.rdt.setHashDbEntry("VoltagesMonHashDb",'chassisId',val)
			status,msg = self.rdt.setHashDbEntry("TemperaturesMonHashDb",'chassisId',val)
			status,msg = self.rdt.setHashDbEntry("PowerSuppliesMonHashDb",'chassisId',val)
			status,msg = self.rdt.setHashDbEntry("FanMonHashData",'chassisId',val)
			status,msg = self.rdt.setHashDbEntry("PowerControlMonHashDb",'chassisId',val)
			# Retrieving one hash dict with key to check if properly inserted or not
			status,msg,test_val = self.rdt.getHashDbEntry("ManagersMonHashDb",'managerId')
		except  redis.ResponseError as e:
			print ("Error: Failure to create Hashes in redis Db")
			return (False, e)
		#Defensive check to see if values are properly inserted or not
		if status and test_val['key1'] == val['key1']:
		 	return True
		else:
			return False


