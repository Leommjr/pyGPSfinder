#!/usr/bin/python
#violet python!!!

import requests
import argparse
from os.path import basename
from bs4 import BeautifulSoup
from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS

def _get_if_exist(data, key):
	#https://gist.github.com/erans/983821/cce3712b82b3de71c73fbce9640e25adef2b0392
    if key in data:
        return data[key]
		
    return None
def _convert_to_degress(value):
	#https://gist.github.com/erans/983821/cce3712b82b3de71c73fbce9640e25adef2b0392
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)

def get_lat_lon(exif_data):
	#https://gist.github.com/erans/983821/cce3712b82b3de71c73fbce9640e25adef2b0392
    """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
    lat = None
    lon = None

    if("GPSInfo" in exif_data):		
        gps_info = exif_data["GPSInfo"]

        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')

        if(gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref):
            lat = _convert_to_degress(gps_latitude)
            if(gps_latitude_ref != "N"):                     
                lat = 0 - lat

            lon = _convert_to_degress(gps_longitude)
            if(gps_longitude_ref != "E"):
                lon = 0 - lon
    else:
    	print("Tem n")
    	print(exif_data)

    return lat, lon

def searchImg(url):
    print("-*- In Url  "+ url)
    urlC = requests.get(url)
    soup = BeautifulSoup(urlC.text,features="html.parser")
    imgT = soup.findAll('img')
    
    return imgT

def downImg(imgT):
    try:
    	print("Downloading image...")
    	imgSrc = imgT['src']
    	imgC = requests.get(imgSrc)
    	imgFileName = imgC.url.split("/")[-1]
    	print(imgFileName)
    	imgFile = open(imgFileName,"wb")
    	imgFile.write(imgC.content)
    	imgFile.close()
    	return imgFileName
    except:
    	return ''

def testForExif(imgFileName):
	try:
		exifD = {}
		imgFile = Image.open(imgFileName)
		imgFile.verify()
		info = imgFile._getexif()
		if(info):
			for(tag,value) in info.items():
				decode = TAGS.get(tag,tag)
				exifD[decode] = value
				if(decode == 'GPSInfo'):
					geo = {}
					print("-*- "+ imgFileName + " contains GPS MetaData")
					for t in value:
						decoded = GPSTAGS.get(t,t)
						geo[decoded] = value[t]
				
					(lat,lon) = get_lat_lon(geo)
					print("Latitude: "+lat+" Longitude: "+ lon)
					
	except(AttributeError):
		print("This file don't support EXIF tags")
		pass
	except:
		pass
	
##################################MAIN###########################################################
url = None
img = None
parser = argparse.ArgumentParser(description='Find the GPS metadata')
parser.add_argument('-u', '--url', dest='url', type=str, help='specify url address')
parser.add_argument('-i', '--img', dest='img', type=str,help='specify image file name')
args= parser.parse_args()
url = args.url
img = args.img
if(url):
	imgTags = searchImg(url)
	for imgT in imgTags:
		print(imgT)
		imgFileName = downImg(imgT)
		testForExif(imgFileName)
else:
	if(img):
		testForExif(img)