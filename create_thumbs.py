import boto
import os

if __name__=="__main__":
	s3 = boto.connect_s3()
	bucket = s3.get_bucket('julianwalford.photo.backup.grouped')
	bucket_thumbs = s3.get_bucket('julianwalford.photo.backup.thumbs')
	for key in bucket:
		basename = os.path.basename(key.name)
		dirname = os.path.dirname(key.name)
		key.get_contents_to_filename(basename)
		thumb_name = '100.'+basename
		print "Resizing",key.name
		subprocess.check_call(['convert','-thumbnail','x100',basename,thumb_name])
		print "Uploading",thumb_name
		thumb_key = boto.s3.key.Key(bucket_thumbs)
		thumb_key.key = '100/'+key.name
		thumb_key.set_contents_from_filename(thumb_name)
		os.remove(basename)
		os.remove(thumb_name)

