
class webex_person:

	def __init__(self,email):
		self.email = email
		self.Questions = []
		self.AskQues = 1
		self.container = email.replace('@','.')
		self.port = None
		self.ip = None


