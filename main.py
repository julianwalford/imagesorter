#!import boto, socket, os, re
from namecache import NameCache
from cStringIO import StringIO
from os.path import normpath,normcase
import subprocess
import PIL,PIL.Image, PIL.ExifTags, boto, re, os
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
new_bucket = conn.get_bucket('julianwalford.photo.backup.grouped')
#cache = NameCache(new_bucket)
for key in bucket.list():
    if key.size==0:
        continue
    print key
    name = key.name
    basename = name.split('/')[-1]
    newname = ''
##    if name.endswith('JPG'): 
##         s = key.get_contents_as_string()
##         img = PIL.Image.open(StringIO(s))
##         exif = {PIL.ExifTags.TAGS[k]: v for k,v in img._getexif().items() if k in PIL.ExifTags.TAGS}
##         day,month,year = ExtractDateJpg(exif)
##         newname = year+"_"+month+"_"+day+'/'+basename
##     if name.endswith('TIF'):
##         s = key.get_contents_as_string()
##         img = ExifFile(StringIO(s))
##         datetime = img['Image DateTime']
## #        re.search(
##         import pdb;pdb.set_trace()
##    if name.upper().endswith('MOV'):
##        basename = os.path.basename(name.upper())
##        base, ext = os.path.splitext(basename)
##        date = cache.get_date(base)
##        if date:
##           newname = '/'.join([date, basename])
    newname = 'ungrouped/'+basename
    if name.upper().endswith('JPG'):
        key.get_contents_to_filename(basename)
        try:
            date = subprocess.check_output(['exiftool','-d', '%Y:%m:%d', '-DateTimeOriginal',basename])
        except subprocess.CalledProcessError, e:
            print "Error extracting date"
            continue
        research = re.search('(?P<year>[0-9]{4}):(?P<month>[0-9]{2}):(?P<day>[0-9]{2})', date)
        if not research: 
            print "No date information found"
            newname = 'ungrouped/'+basename
        else:
            day, month, year = research.group('day'), research.group('month'), research.group('year')
            print basename, day, month, year
            newname = year+'_'+month+"_"+day+"/"+basename
        os.remove(basename)
    if name.upper().endswith('MP4'):
        research = re.search('(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})',name)
        if not research:
            print "No date information found"
            continue
        else:
            day, month, year = research.group('day'), research.group('month'), research.group('year')
            print basename, day, month, year
            newname = year+'_'+month+'_'+day+"/"+basename

    
    if newname:
        if newname.endswith('TIF'):
            #check of RW2 key already exists -- skip move
            if new_bucket.get_key(newname.replace('TIF','RW2')):
                print "Deleting duplicate key"
                key.delete()
                continue
        print "Moving",basename,"to",newname
        new_key = key.copy('julianwalford.photo.backup.grouped',newname)
        if new_key.exists:
            key.delete()

