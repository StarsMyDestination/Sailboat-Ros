#!/usr/bin/python
# -*- coding: utf-8 -*-

from math import *
import rospy
from std_msgs.msg import String
from   sailboat_message.msg import GPS_msg
import serial
import struct
import logging


# gnss receiver address
# if using serial port, set it something like to "COM1" or "/dev/tty1"
GNSS_URL = "/dev/ttyUSB0"
# serial port baudrate
BAUDRATE = 115200
# connection timeout in seconds
TIMEOUT = 2
# commands sent to GNSS receiver
INIT_COMMANDS = """UNLOGALL
LOG BESTPOSA ontime 0.2
LOG BESTVELA ontime 0.2
"""
#INIT_COMMANDS = """UNLOGALL"""
# lat/lon of original point, use to caculate posx/posy (north and east are positive)
ORIGIN_LAT = 31.0231632
ORIGIN_LON = 121.4251289



novatel_tbl = (
    0x00000000L, 0x77073096L, 0xee0e612cL, 0x990951baL, 0x076dc419L, 0x706af48fL,
    0xe963a535L, 0x9e6495a3L, 0x0edb8832L, 0x79dcb8a4L, 0xe0d5e91eL, 0x97d2d988L,
    0x09b64c2bL, 0x7eb17cbdL, 0xe7b82d07L, 0x90bf1d91L, 0x1db71064L, 0x6ab020f2L,
    0xf3b97148L, 0x84be41deL, 0x1adad47dL, 0x6ddde4ebL, 0xf4d4b551L, 0x83d385c7L,
    0x136c9856L, 0x646ba8c0L, 0xfd62f97aL, 0x8a65c9ecL, 0x14015c4fL, 0x63066cd9L,
    0xfa0f3d63L, 0x8d080df5L, 0x3b6e20c8L, 0x4c69105eL, 0xd56041e4L, 0xa2677172L,
    0x3c03e4d1L, 0x4b04d447L, 0xd20d85fdL, 0xa50ab56bL, 0x35b5a8faL, 0x42b2986cL,
    0xdbbbc9d6L, 0xacbcf940L, 0x32d86ce3L, 0x45df5c75L, 0xdcd60dcfL, 0xabd13d59L,
    0x26d930acL, 0x51de003aL, 0xc8d75180L, 0xbfd06116L, 0x21b4f4b5L, 0x56b3c423L,
    0xcfba9599L, 0xb8bda50fL, 0x2802b89eL, 0x5f058808L, 0xc60cd9b2L, 0xb10be924L,
    0x2f6f7c87L, 0x58684c11L, 0xc1611dabL, 0xb6662d3dL, 0x76dc4190L, 0x01db7106L,
    0x98d220bcL, 0xefd5102aL, 0x71b18589L, 0x06b6b51fL, 0x9fbfe4a5L, 0xe8b8d433L,
    0x7807c9a2L, 0x0f00f934L, 0x9609a88eL, 0xe10e9818L, 0x7f6a0dbbL, 0x086d3d2dL,
    0x91646c97L, 0xe6635c01L, 0x6b6b51f4L, 0x1c6c6162L, 0x856530d8L, 0xf262004eL,
    0x6c0695edL, 0x1b01a57bL, 0x8208f4c1L, 0xf50fc457L, 0x65b0d9c6L, 0x12b7e950L,
    0x8bbeb8eaL, 0xfcb9887cL, 0x62dd1ddfL, 0x15da2d49L, 0x8cd37cf3L, 0xfbd44c65L,
    0x4db26158L, 0x3ab551ceL, 0xa3bc0074L, 0xd4bb30e2L, 0x4adfa541L, 0x3dd895d7L,
    0xa4d1c46dL, 0xd3d6f4fbL, 0x4369e96aL, 0x346ed9fcL, 0xad678846L, 0xda60b8d0L,
    0x44042d73L, 0x33031de5L, 0xaa0a4c5fL, 0xdd0d7cc9L, 0x5005713cL, 0x270241aaL,
    0xbe0b1010L, 0xc90c2086L, 0x5768b525L, 0x206f85b3L, 0xb966d409L, 0xce61e49fL,
    0x5edef90eL, 0x29d9c998L, 0xb0d09822L, 0xc7d7a8b4L, 0x59b33d17L, 0x2eb40d81L,
    0xb7bd5c3bL, 0xc0ba6cadL, 0xedb88320L, 0x9abfb3b6L, 0x03b6e20cL, 0x74b1d29aL,
    0xead54739L, 0x9dd277afL, 0x04db2615L, 0x73dc1683L, 0xe3630b12L, 0x94643b84L,
    0x0d6d6a3eL, 0x7a6a5aa8L, 0xe40ecf0bL, 0x9309ff9dL, 0x0a00ae27L, 0x7d079eb1L,
    0xf00f9344L, 0x8708a3d2L, 0x1e01f268L, 0x6906c2feL, 0xf762575dL, 0x806567cbL,
    0x196c3671L, 0x6e6b06e7L, 0xfed41b76L, 0x89d32be0L, 0x10da7a5aL, 0x67dd4accL,
    0xf9b9df6fL, 0x8ebeeff9L, 0x17b7be43L, 0x60b08ed5L, 0xd6d6a3e8L, 0xa1d1937eL,
    0x38d8c2c4L, 0x4fdff252L, 0xd1bb67f1L, 0xa6bc5767L, 0x3fb506ddL, 0x48b2364bL,
    0xd80d2bdaL, 0xaf0a1b4cL, 0x36034af6L, 0x41047a60L, 0xdf60efc3L, 0xa867df55L,
    0x316e8eefL, 0x4669be79L, 0xcb61b38cL, 0xbc66831aL, 0x256fd2a0L, 0x5268e236L,
    0xcc0c7795L, 0xbb0b4703L, 0x220216b9L, 0x5505262fL, 0xc5ba3bbeL, 0xb2bd0b28L,
    0x2bb45a92L, 0x5cb36a04L, 0xc2d7ffa7L, 0xb5d0cf31L, 0x2cd99e8bL, 0x5bdeae1dL,
    0x9b64c2b0L, 0xec63f226L, 0x756aa39cL, 0x026d930aL, 0x9c0906a9L, 0xeb0e363fL,
    0x72076785L, 0x05005713L, 0x95bf4a82L, 0xe2b87a14L, 0x7bb12baeL, 0x0cb61b38L,
    0x92d28e9bL, 0xe5d5be0dL, 0x7cdcefb7L, 0x0bdbdf21L, 0x86d3d2d4L, 0xf1d4e242L,
    0x68ddb3f8L, 0x1fda836eL, 0x81be16cdL, 0xf6b9265bL, 0x6fb077e1L, 0x18b74777L,
    0x88085ae6L, 0xff0f6a70L, 0x66063bcaL, 0x11010b5cL, 0x8f659effL, 0xf862ae69L,
    0x616bffd3L, 0x166ccf45L, 0xa00ae278L, 0xd70dd2eeL, 0x4e048354L, 0x3903b3c2L,
    0xa7672661L, 0xd06016f7L, 0x4969474dL, 0x3e6e77dbL, 0xaed16a4aL, 0xd9d65adcL,
    0x40df0b66L, 0x37d83bf0L, 0xa9bcae53L, 0xdebb9ec5L, 0x47b2cf7fL, 0x30b5ffe9L,
    0xbdbdf21cL, 0xcabac28aL, 0x53b39330L, 0x24b4a3a6L, 0xbad03605L, 0xcdd70693L,
    0x54de5729L, 0x23d967bfL, 0xb3667a2eL, 0xc4614ab8L, 0x5d681b02L, 0x2a6f2b94L,
    0xb40bbe37L, 0xc30c8ea1L, 0x5a05df1bL, 0x2d02ef8dL)

# crc
def novatel_crc32(data):
    tbl = novatel_tbl
    crc = 0L
    for c in data:
        crc = tbl[(crc^ord(c))&0xff]^(crc>>8)
    return crc

def d2r(d):
    return d/180.0*pi


class GNSS_ERROR(Exception):
    pass

class GNSS:
    def __init__(self,url,baudrate,timeout,cmds,logger):
        self.url = url
        self.logger = logger
        self.cmds = cmds
        self.ser = serial.serial_for_url(url,do_not_open=True, baudrate=baudrate, timeout=timeout)
        self.open()
        self.isGetData = False

    def set_origin(self, lat,lon):
        self.lat = d2r(lat)
        self.lon = d2r(lon)

    def w84_calc_ne(self, lat2, lon2):
        lat1,lon1 = self.lat,self.lon
        lat2,lon2 = d2r(lat2),d2r(lon2)
        d_lat = lat2-lat1
        d_lon = lon2-lon1

        a = 6378137.0
        e_2 = 6.69437999014e-3
        r1 = a*(1-e_2)/(1-e_2*(sin(lat1))**2)**1.5
        r2 = a/sqrt(1-e_2*(sin(lat1))**2)

        north = r1*d_lat
        east = r2*cos(lat1)*d_lon
        return north,east

    def close(self):
        self.logger.info('GNSS close: '+self.url)
        self.ser.close()

    def open(self):
        self.logger.info('GNSS open: '+self.url)
        self.line = ''
        self.ser.open()
        if self.cmds!=None and self.cmds!= "":
            self.ser.write(self.cmds.replace("\r","").replace("\n","\r\n"))

    def update(self):
        l = self.ser.readline()
        print l
        if l == '':
            self.logger.warning('GNSS timeout, reconnect')
            self.close()
            self.open()
        self.line = self.line + l
        if self.line.endswith('\n'):
            # a new line received
            self.parse_line()
            self.line = ''

    def parse_line(self):
        if not self.line.startswith('#'):
            return
        self.line = self.line.rstrip('\r\n')
        if not self.nv_validate():
            return
        self.parse_header()
        self.parse_content()

    def parse_header(self):
        ps = self.header.split(',')
        if len(ps)!= 10:
            raise GNSS_ERROR('invalid novatel header '+self.header)

        self.time = float(ps[6])
        self.logtype = ps[0].upper()

    def parse_content(self):
        if self.logtype == "BESTPOSA":
            self.parse_bestposa()
        elif self.logtype == "BESTVELA":
            self.parse_bestvela()

    def parse_bestposa(self):
        ps = self.content.split(',')
        if len(ps)!=21:
            raise GNSS_ERROR('invalid bestposa '+self.content)
        if ps[1]=='NONE' or ps[0]!='SOL_COMPUTED':
            self.posx, self.posy, self.posz = 0,0,0
            self.stdx, self.stdy, self.stdz = 0,0,0
            self.satn = 0
            return

        isGetData =True
        lat,lon = float(ps[2]),float(ps[3])
        self.posx,self.posy = self.w84_calc_ne(lat,lon)
        self.posz = float(ps[4])

        self.stdx,self.stdy,self.stdz = float(ps[7]),float(ps[8]),float(ps[9])

        self.satn = float(ps[14])

        print('pos = ', self.posx, '  and ', self.posy)

    def parse_bestvela(self):
        ps = self.content.split(',')
        if len(ps)!=8:
            raise GNSS_ERROR('invalid bestvela '+self.content)
        if ps[1]=='NONE' or ps[0]!='SOL_COMPUTED':
            self.hspeed = 0
            self.vspeed = 0
            self.track = 0
            return
        self.hspeed = float(ps[4])
        self.track = float(ps[5])/180*pi
        self.vspeed = float(ps[6])


    def nv_validate(self):
        line = self.line.lstrip('#')
        if len(line)<20 or line[-9]!='*':
            self.logger.warning('invalid novatel log: '+line)
            return False

        ps = line.split(';')
        if len(ps)!=2 :
            self.logger.warning('invalid novatel log: '+line)
            return False
        self.header = ps[0]

        ps = ps[1].split('*')
        if len(ps)!=2 :
            self.logger.warning('invalid novatel log: '+line)
            return False
        self.content = ps[0]

        try:
            cksum = int(ps[1],16)
        except ValueError:
            self.logger.warning('invalid novatel cksum: '+ps[1])
            return False
        if cksum != novatel_crc32(self.header+';'+self.content):
            self.logger.warning('invalid novatel cksum: '+ps[1])
            return False    

        return True

def console_logger():
    # create logger
    logger = logging.getLogger("gnss")
    logger.setLevel(logging.INFO)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger


def talker():#ros message publish
    pub = rospy.Publisher('gps', GPS_msg, queue_size=5)
    rospy.init_node('gps_talker', anonymous=True)
    rate = rospy.Rate(5) # 5hz

    logger = console_logger() #todo write in Class GNSS
    gnss = GNSS(GNSS_URL, BAUDRATE, TIMEOUT, INIT_COMMANDS, logger) 
    gnss.set_origin(ORIGIN_LAT,ORIGIN_LON)
    try:
        while not rospy.is_shutdown():
            gnss.update()
            gnss.update()
            if gnss.isGetData == True:
                GPS_msg.timestamp = rospy.get_time()
                GPS_msg.satn = gnss.satn
                GPS_msg.posx = gnss.posx
                GPS_msg.posy = gnss.posy
                GPS_msg.posz = gnss.posz
                GPS_msg.stdx = gnss.stdx
                GPS_msg.stdy = gnss.stdy
                GPS_msg.stdz = gnss.stdz
                GPS_msg.hspeed = gnss.hspeed
                GPS_msg.track = gnss.track
                GPS_msg.vspeed = gnss.vspeed
                rospy.loginfo(GPS_msg.posx)
                pub.publish(GPS_msg)
                rate.sleep()
    except rospy.ROSInterruptException:
        pass
    finally:
        gnss.close()


if __name__ == "__main__":
    talker()