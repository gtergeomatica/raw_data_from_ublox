#!/usr/bin/env python
# Copyleft Gter srl 2019
#Lorenzo Benvenuto


import sys,os
import time
from datetime import datetime, timedelta
import psutil
import shutil #shell utilities
import errno
from ftplib import FTP
from credenziali import *


class GNSSReceiver:
    '''This class describes the possibile action that a generic GNSS receiver connected to a microprocessor can do'''
    
    def __init__(self, out_raw="default_filename", model="Ublox neo m8t", antenna="patch", serial="ttyACM0", raw_format="ubx",repo_absolute_path="/home/pi/REPOSITORY/raw_data_from_ublox/",rtklib_path='/home/pi/RTKLIB/',st_coord=()):
        self.model=model
        self.antenna=antenna
        self.serial=serial
        self.raw_format=raw_format
        self.out_raw=out_raw
        self.repo_absolute_path=repo_absolute_path #the path where the repository has been cloned
        self.rtklib_path=rtklib_path
        self.st_coord=st_coord #approximate XYZ (ECEF) station coordinates
        
    def __str__(self):
        return "\tReceiver: %s\n\tAntenna: %s\n\tSerial: %s\n\tGNSS raw format: %s\n\tGNSS raw data file: ./output_ubx/%s\n\trtklib path: %s\n"%(self.model,self.antenna,self.serial,self.raw_format,self.out_raw,self.rtklib_path)


    def RecordRaw(self):
        ''' Method to record raw GNSS data from a ublox receiver.
            The receiver configuration is not set in this script and must be set using the u-center software
            Input parameters:
            - time 
            
            The raw GNSS data are saved by default in the ubx format in the folder ./output_ubx
    '''
        #time_min = 1 #time for raw data recording
        #time_sec = time_min*60
        out_file = "%s/output_ubx/%s.%s"%(os.path.dirname(os.path.realpath(__file__)),self.out_raw,self.raw_format)
        print(out_file)    
        str2str_path="%sapp/str2str/gcc/str2str"%(self.rtklib_path) #path to str2str executable
        run_str2str = "%s -in serial://%s#%s -out file://%s -out tcpsvr://:8081 &" %(str2str_path, self.serial, self.raw_format, out_file)
        
        time.sleep(2)
        print("\n************* Start data acquisition *************\n")

        os.system(run_str2str)
        
        a = []
        time.sleep(2)
        process = filter(lambda p: p.name() == "str2str", psutil.process_iter())
        for i in process:
            a.append(i.pid)
            print (i.name, i.pid, a)


        process_ID = a[-1] #if there are more str2str procces, the PID are appended in this array. The PID of the str2srt proccess launched by this script is the last element of the array.
        #print (process_ID)
        
        return process_ID

    def FunctionTest(parmeter):
            output_test_param="test_%s" %(parmeter)
            return output_test_param

    def RinexConverter(self,marker,comment,rinex_name_obs,rinex_name_nav):

        '''Function to convert a raw GNSS file from ubx format to RINEX format using CONVBIN module of rtklib

    '''
        if type(self.st_coord) != tuple:
            print('station coordinates must be in a tuple (x,y,x)')
            return
        else:
            infile = "%s/output_ubx/%s.%s"%(os.path.dirname(os.path.realpath(__file__)),self.out_raw,self.raw_format)
            outfile_obs = "%s/output_rinex/%s"%(os.path.dirname(os.path.realpath(__file__)),rinex_name_obs)
            outfile_nav = "%s/output_rinex/%s"%(os.path.dirname(os.path.realpath(__file__)),rinex_name_nav)
            convbin_path="%sapp/convbin/gcc/convbin"%(self.rtklib_path)
            #marker = "'LIGE'"
            #comment = "'LIDAR ITALIA GNSS Permanent Station'"
            #receiver = "'Ublox ZED F9P'"
            #antenna = "'HEMISPHERE A45'"
        
    
            run_convbin_obs = "%s %s -o %s -n %s -od -os -hc %s -hm %s -hr '%s' -ha '%s' -hp %s/%s/%s -v 3.02"%(convbin_path, infile, outfile_obs, outfile_nav, comment, marker, self.model, self.antenna, self.st_coord[0], self.st_coord[1],self.st_coord[2])
            print(run_convbin_obs)
            print("\n************* Conversion ubx --> RINEX *************\n")
            os.system(run_convbin_obs)
            print("\n************* Done! *************\n")
            return(outfile_obs)

    def removeRinex(self, filename):
        try:
            os.system('rm {}/output_rinex/{}'.format(os.path.dirname(os.path.realpath(__file__)),filename))
            return True
        except Exception as e:
            print(e)
            return False
    
    def removeBinary(self):
        try:
            os.system('rm {}/output_ubx/{}.{}'.format(os.path.dirname(os.path.realpath(__file__)),self.out_raw,self.raw_format))
            return True
        except Exception as e:
            print(e)
            return False
    
    
    
    
    def Hatanaka():
        '''Function to compress a RINEX file using the hatanaka compression format
        
    '''
        pass


def rinex302filename(st_code,ST,session_interval,obs_freq,data_type,data_type_flag,bin_flag,data_format='RINEX',compression=None):
    '''function to dynamically define the filename in rinex 3.02 format)
    Needed parameters
    1: STATION/PROJECT NAME (SPN); format XXXXMRCCC
        XXXX: station code
        M: monument or marker number (0-9)
        R: receiver number (0-9)
        CCC:  ISO Country CODE see ISO 3166-1 alpha-3 
    
    2: DATA SOURCE (DS)
        R – From Receiver data using vendor or other software
        S – From data Stream (RTCM or other)
        U – Unknown (1 character)
    
    3: START TIME (ST); fomrat YYYYDDDHHMM (UTC)
        YYYY - Gregorian year 4 digits,
        DDD  – day of year,
        HHMM - Hour and minutes of day
    4: FILE PERIOD (FP): format DDU
        DD – file period 
        U – units of file period.
        Examples:
        15M – 15 Minutes 
        01H – 1 Hour
        01D – 1 Day
        01Y – 1 Year 
        00U - Unspecified
    
    5: DATA FREQ (DF); format DDU
        DD – data frequency 
        U – units of data rate 
        Examples:
        XXS – Seconds,
        XXM – Minutes,
        XXH – Hours,
        XXD – Days
        XXU – Unspecified
    6: DATA TYPE (DT); format DD (default value are MO for obs and MN for nav)
        GO - GPS Obs.,
        RO - GLONASS Obs., 
        EO - Galileo Obs. 
        JO - QZSS Obs., 
        CO - BDS Obs., 
        IO – IRNSS Obs., 
        SO - SBAS Obs., 
        MO Mixed Obs., 
        GN - Nav. GPS, 
        RN- Glonass Nav., 
        EN- Galileo Nav., 
        JN- QZSS Nav., 
        CN- BDS Nav., 
        IN – IRNSS Nav., 
        SN- SBAS Nav., 
        MN- Nav. All GNSS Constellations 
        MM-Meteorological Observation 
        Etc
    7: FORMAT
        Three character indicating the data format:
        RINEX - rnx, 
        Hatanaka Compressed RINEX – crx, 
        ETC
    
    8: COMPRESSION
        .zip
        .gz
        .tar.gz
        etc
        if None the filename will ends with .YYO
    '''
    filename=''

    # STATION/PROJECT NAME

    M=0 #master
    R=0 #rover

    if st_code=='SAOR':
        CCC='FRA'
    else:
        CCC='ITA'
    
    SPN='{}{}{}{}_'.format(st_code,M,R,CCC)

    filename+=SPN

    # DATA SOURCE 
    DS='R'
    filename+='{}_'.format(DS)

    # START TIME
    filename+='{}_'.format(ST)
    

    # FILE PERIOD
    interval=timedelta(seconds=session_interval*60)

    if interval.days != 0 and interval.seconds//3600 ==0:
        FP='%02dD'%(interval.days)
    elif interval.days == 0 and interval.seconds//3600 !=0:
        FP='%02dH'%(interval.seconds//3600)
    else:
        FP='00U'

    filename+='{}_'.format(FP)

    # DATA FREQ
    
    freq=timedelta(seconds=obs_freq)
    #print(freq)
    #print((freq.seconds//60)%60,freq.seconds)
    if freq.seconds!=0 and (freq.seconds//60)%60==0:
        DF='%02dS'%(freq.seconds)
    elif freq.seconds==0 and (freq.seconds//60)%60!=0:
        DF='%02dM'%((freq.seconds//60)%60)
    else:
        DF='00U'

    filename+='{}'.format(DF)

    # DATA TYPE
    if data_type_flag:
        if data_type =='MN':
            filename=filename[:-4]+'_MN.rnx'
            return filename
        filename+='_{}.rnx'.format(data_type)
        #parte per compressione
    else:
        filename+='_{}.rnx'
        
            
    
    return filename
