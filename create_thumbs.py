import boto
import os
import subprocess

def createTIFfromRAW(basename):
    curdir = os.getcwd()
    dcraw = os.path.normpath(os.path.join(curdir,'..','dcraw','dcraw'))
    subprocess.check_call([dcraw,'-T',os.path.join(os.getcwd(),basename)])
    return basename.replace('RW2','tiff')

if __name__=="__main__":
    #Get connected
    s3 = boto.connect_s3()

    #Where we are reading the full images from, and writing the thumbs to
    bucket = s3.get_bucket('julianwalford.photo.backup.grouped')
    bucket_thumbs = s3.get_bucket('julianwalford.photo.backup.thumbs')

    #Start copying, key by key
    for key in bucket:
        localkeyname = keyname = key.name
        localbasename = basename = os.path.basename(keyname)
        thumb_name = '100.'+localbasename
        new_key_name = '100/'+localkeyname
        if bucket_thumbs.get_key(new_key_name): 
            print "Found existing thumbnail for ",keyname
            continue

        #Download file and prepare to convert
        key.get_contents_to_filename(basename)
        if basename.endswith('.RW2'):
            localbasename = createTIFfromRAW(basename)

        #Resize
        print "Resizing",keyname
        subprocess.check_call(['convert','-thumbnail','x100',localbasename,thumb_name])

        #Upload
        print "Uploading",thumb_name
        thumb_key = boto.s3.key.Key(bucket_thumbs)
        thumb_key.key = new_key_name
        thumb_key.set_contents_from_filename(thumb_name)

        #Clean up
        os.remove(basename)
        os.remove(thumb_name)

