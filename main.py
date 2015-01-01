#!import boto, socket, os, re
from cStringIO import StringIO
from os.path import normpath,normcase
import subprocess
import PIL,PIL.Image, PIL.ExifTags, boto, re
from EXIF import process_file as ExifFile

def extractDateJpg(exif):
    date = exif['DateTimeOriginal']
    rematch = re.match('(?P<year>[0-9]{4}):(?P<month>[0-9]{2}):(?P<day>[0-9]{2}) [0-9]{2}:[0-9]{2}:[0-9]{2}',date)
    day,month,year = rematch.group('day'),rematch.group('month'),rematch.group('year')
    return day,month,year

def extractDateTif(exif):
    date = exif['Image DateTime']
    research = re.search('ASCII=(?P<year>[0-9]{4}):(?P<month>[0-9]{2}):(?P<day>[0-9]{2})',date)
    day,month,year = research.group('day'),research.group('month'),research.group('year')
conn = boto.connect_s3()
print "Connected to S3"

bucket = conn.get_bucket('julianwalford.photo.backup')
for key in bucket.list():
    print key
    basename = key.name.split('/')[-1]
    newname = ''
    if key.name.endswith('JPG'): 
        s = key.get_contents_as_string()
        img = PIL.Image.open(StringIO(s))
        exif = {PIL.ExifTags.TAGS[k]: v for k,v in img._getexif().items() if k in PIL.ExifTags.TAGS}
        day,month,year = ExtractDateJpg(exif)
        newname = year+"_"+month+"_"+day+'/'+basename
    if key.name.endswith('TIF'):
        s = key.get_contents_as_string()
        img = ExifFile(StringIO(s))
        datetime = img['Image DateTime']
#        re.search(
        import pdb;pdb.set_trace()


    if newname:
        new_key = key.copy('julianwalford.photo.backup.grouped',newname)
        if new_key.exists:
            key.delete()
    
