import boto

class NameCache:
	def __init__(self,bucket):
		self.cache = {}
		for key in bucket.list():
			if '/' in key.name:
				date, name = key.name.split('/')
				if '.' in name:
					base, ext = name.split('.')
				else:
					base = name
				self.cache[base] = date

	def get_date(self, name):
		return self.cache.get(name,'')


if __name__=="__main__":
	conn = boto.connect_s3()
	print "Connected to S3"

	bucket = conn.get_bucket('julianwalford.photo.backup.grouped')
	n = NameCache(bucket)
