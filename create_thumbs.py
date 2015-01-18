import boto
import os
import subprocess

if __name__=="__main__":
    s3 = boto.connect_s3()
    bucket = s3.get_bucket('julianwalford.photo.backup.grouped')
    bucket_thumbs = s3.get_bucket('julianwalford.photo.backup.thumbs')
    for key in bucket:
        localkeyname = keyname = key.name
        localbasename = basename = os.path.basename(keyname)
        if basename.endswith('.RW2'):
            localbasename = basename.replace('RW2','tiff')
            localkeyname = keyname.replace('RW2','tiff')
        thumb_name = '100.'+localbasename
        new_key_name = '100/'+localkeyname
        if bucket_thumbs.get_key(new_key_name): 
            print "Found existing thumbnail for ",keyname
            continue
        key.get_contents_to_filename(basename)
        if basename.endswith('.RW2'):
            curdir = os.getcwd()
            dcraw = os.path.normpath(os.path.join(curdir,'..','dcraw','dcraw'))
            subprocess.check_call([dcraw,'-T',os.path.join(os.getcwd(),basename)])
        print "Resizing",keyname
        subprocess.check_call(['convert','-thumbnail','x100',localbasename,thumb_name])
        print "Uploading",thumb_name
        thumb_key = boto.s3.key.Key(bucket_thumbs)
        thumb_key.key = new_key_name
        thumb_key.set_contents_from_filename(thumb_name)
        os.remove(basename)
        os.remove(thumb_name)

