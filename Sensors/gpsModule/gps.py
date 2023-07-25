#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This code is generated by scons.  Do not hand-hack it!
"""gps.py -- Python interface to GPSD.

This interface has a lot of historical cruft in it related to old
protocol, and was modeled on the C interface. It won't be thrown
away, but it's likely to be deprecated in favor of something more
Pythonic.

The JSON parts of this (which will be reused by any new interface)
now live in a different module.
"""

#
# This file is Copyright 2010 by the GPSD project
# SPDX-License-Identifier: BSD-2-Clause
#

# This code runs compatibly under Python 2 and 3.x for x >= 2.
# Preserve this property!
from __future__ import absolute_import, print_function, division
import argparse
import binascii      # for binascii.hexlify()
import os            # for file handling in gps_io
import socket        # for socket.error
import stat          # for stat.S_ISBLK()
import sys           # to get script name for nice error/warning messages

from .misc import monotonic, polybytes
from .client import *
from .watch_options import *


# Sometimes used in gps_io if a serial device is specified
try:
    import serial
except ImportError:
    serial = None  # Defer complaining until we know we need it.

NaN = float('nan')



def isfinite(f):
    """Check if f is finite."""
    # Python 2 does not think +Inf or -Inf are NaN
    # Python 2 has no easier way to test for Inf
    return float('-inf') < float(f) < float('inf')

VERB_QUIET = 0   # quiet
VERB_NONE = 1    # just output requested data and some info
VERB_DECODE = 2  # decode all messages
VERB_INFO = 3    # more info
VERB_RAW = 4     # raw info
VERB_PROG = 5    # program trace
test = 1234

# Don't hand-hack this list, it's generated.
ONLINE_SET = (1 << 1)
TEST_SET = (1 << 1)

TIME_SET = (1 << 2)
TIMERR_SET = (1 << 3)
LATLON_SET = (1 << 4)
ALTITUDE_SET = (1 << 5)
SPEED_SET = (1 << 6)
TRACK_SET = (1 << 7)
CLIMB_SET = (1 << 8)
STATUS_SET = (1 << 9)
MODE_SET = (1 << 10)
DOP_SET = (1 << 11)
HERR_SET = (1 << 12)
VERR_SET = (1 << 13)
ATTITUDE_SET = (1 << 14)
SATELLITE_SET = (1 << 15)
SPEEDERR_SET = (1 << 16)
TRACKERR_SET = (1 << 17)
CLIMBERR_SET = (1 << 18)
DEVICE_SET = (1 << 19)
DEVICELIST_SET = (1 << 20)
DEVICEID_SET = (1 << 21)
RTCM2_SET = (1 << 22)
RTCM3_SET = (1 << 23)
AIS_SET = (1 << 24)
PACKET_SET = (1 << 25)
SUBFRAME_SET = (1 << 26)
GST_SET = (1 << 27)
VERSION_SET = (1 << 28)
POLICY_SET = (1 << 29)
LOGMESSAGE_SET = (1 << 30)
ERROR_SET = (1 << 31)
TIMEDRIFT_SET = (1 << 32)
EOF_SET = (1 << 33)
SET_HIGH_BIT = 34
UNION_SET = (RTCM2_SET | RTCM3_SET | SUBFRAME_SET | AIS_SET | VERSION_SET |
             DEVICELIST_SET | ERROR_SET | GST_SET)
STATUS_NO_FIX = 0
STATUS_FIX = 1
STATUS_DGPS_FIX = 2
STATUS_RTK_FIX = 3
STATUS_RTK_FLT = 4
STATUS_DR = 5
STATUS_GNSSDR = 6
STATUS_TIME = 7
STATUS_SIM = 8
STATUS_PPS_FIX = 9
MODE_NO_FIX = 1
MODE_2D = 2
MODE_3D = 3
MAXCHANNELS = 72  # Copied from gps.h, but not required to match
SIGNAL_STRENGTH_UNKNOWN = NaN


class gpsfix(object):
    """Class to hold one GPS fix."""

    def __init__(self):
        """Init class gpsfix."""

        self.altitude = NaN         # Meters DEPRECATED
        self.altHAE = NaN           # Meters
        self.altMSL = NaN           # Meters
        self.climb = NaN            # Meters per second
        self.datum = ""
        self.dgpsAge = -1
        self.dgpsSta = ""
        self.depth = NaN
        self.device = ""
        self.ecefx = NaN
        self.ecefy = NaN
        self.ecefz = NaN
        self.ecefvx = NaN
        self.ecefvy = NaN
        self.ecefvz = NaN
        self.ecefpAcc = NaN
        self.ecefvAcc = NaN
        self.epc = NaN
        self.epd = NaN
        self.eph = NaN
        self.eps = NaN
        self.ept = NaN
        self.epv = NaN
        self.epx = NaN
        self.epy = NaN
        self.geoidSep = NaN        # Meters
        self.latitude = self.longitude = 0.0
        self.magtrack = NaN
        self.magvar = NaN
        self.mode = MODE_NO_FIX
        self.relN = NaN
        self.relE = NaN
        self.relD = NaN
        self.sep = NaN              # a.k.a. epe
        self.speed = NaN            # Knots
        self.status = STATUS_NO_FIX
        self.time = NaN
        self.track = NaN            # Degrees from true north
        self.velN = NaN
        self.velE = NaN
        self.velD = NaN


class gps_io(object):
    """All the GPS I/O in one place.

    Three types of GPS I/O
    1. read only from a file
    2. read/write through a device
    3. read only from a gpsd instance
"""

    out = b''
    ser = None
    input_is_device = False

    def __init__(self, input_file_name=None, read_only=False,
                 gpsd_host='localhost', gpsd_port=2947,
                 gpsd_device=None,
                 input_speed=9600,
                 verbosity_level=0,
                 write_requested=True):
        """Initialize class.

    Arguments:
      input_file_name: Name of a device/file to open - None if connection to
                       gpsd via network
      read_only: request a read only access (will be set automagically when
                 a file is used for input)
      gpsd_host: hostname of host running the gpsd
      gpsd_port: port of [hostname] running the gpsd
      gpsd_device: Specify a dedicated device for the gpsd - None for auto
      input_speed: If input_file_name is a (serial) device this specifies
                   the speed in baud
      verbosity_level: Specify the verbosity level (0..5)
      write_requested: Set to true if a write operation shall be executed
                       (used for internal sanity checking)
"""

        self.gpsd_device = gpsd_device
        # Used as an indicator in read if a device, file or network connection
        # is used
        self.gpsd_host = gpsd_host
        self.gpsd_port = gpsd_port
        # required by write for packet construction
        self.gpsd_device = gpsd_device
        # used in read to print meaningfull error
        self.input_file_name = input_file_name
        self.verbosity_level = verbosity_level
        self.prog_name = os.path.basename(sys.argv[0])
        Serial = serial
        Serial_v3 = Serial and Serial.VERSION.split('.')[0] >= '3'
        # buffer to hold read data
        self.out = b''

        if VERB_PROG <= verbosity_level:
            print('gps_io(gpsd_device=%s gpsd_host=%s gpsd_port=%s\n'
                  '       input_file_name=%s input_speed=%s read_only=%s\n'
                  '       verbosity_level=%s write_requested=%s)' %
                  (gpsd_device, gpsd_host, gpsd_port,
                   input_file_name, input_speed, read_only,
                   verbosity_level, write_requested))

        # open the input: device, file, or gpsd
        if input_file_name is not None:
            # check if input file is a file or device
            try:
                mode = os.stat(input_file_name).st_mode
            except OSError:
                sys.stderr.write('%s: failed to open input file %s\n' %
                                 (self.prog_name, input_file_name))
                sys.exit(1)

            if stat.S_ISCHR(mode):
                # character device, need not be read only
                self.input_is_device = True

            # FIXME: test broken
            #if write_requested:
            #    # check for inconsistend arguments
            #    if read_only:
            #        sys.stderr.write('%s: read-only mode, '
            #                         'can not send commands\n' %
            #                         self.prog_name)
            #        sys.exit(1)
            #    # check if a file instead of device was specified
            #    if self.input_is_device is False:
            #        sys.stderr.write('%s: input is plain file, '
            #                         'can not send commands\n' %
            #                         self.prog_name)
            #        sys.exit(1)

        else:
            # try to open local/remote gpsd daemon over tcp
            if not self.gpsd_host:
                self.gpsd_host = 'localhost'
            try:
                self.ser = gpscommon(host=self.gpsd_host,
                                     input_file_name=input_file_name,
                                     port=self.gpsd_port,
                                     verbose=self.verbosity_level)

                # alias self.ser.write() to self.write_gpsd()
                self.ser.write = self.write_gpsd

                # ask for raw, not rare, data
                data_out = b'?WATCH={'
                if gpsd_device is not None:
                    # add in the requested device
                    data_out += (b'"device":"' +
                                 polybytes(gpsd_device) +
                                 b'",')
                data_out += b'"enable":true,"raw":2}\r\n'
                if VERB_RAW <= verbosity_level:
                    print("sent: ", data_out)
                self.ser.send(data_out)
            except socket.error as err:
                sys.stderr.write('%s: failed to connect to gpsd %s\n' %
                                 (self.prog_name, err))
                sys.exit(1)
            return

        if self.input_is_device:
            # configure the serial connections (the parameters refer to
            # the device you are connecting to)

            # pyserial Ver 3.0+ changes writeTimeout to write_timeout
            # Using the wrong one causes an error
            write_timeout_arg = ('write_timeout'
                                 if Serial_v3 else 'writeTimeout')
            try:
                self.ser = Serial.Serial(
                    baudrate=input_speed,
                    # 8N1 is UBX default
                    bytesize=Serial.EIGHTBITS,
                    parity=Serial.PARITY_NONE,
                    port=input_file_name,
                    stopbits=Serial.STOPBITS_ONE,
                    # read timeout
                    timeout=0.05,
                    **{write_timeout_arg: 0.5}
                )
            except AttributeError:
                sys.stderr.write('%s: failed to import pyserial\n' %
                                 self.prog_name)
                sys.exit(2)
            except Serial.serialutil.SerialException:
                # this exception happens on bad serial port device name
                sys.stderr.write('%s: failed to open serial port "%s"\n'
                                 '%s: Your computer has the serial ports:\n' %
                                 (self.prog_name, input_file_name,
                                  self.prog_name))

                # print out list of supported ports
                # FIXME: bad location for an import
                import serial.tools.list_ports as List_Ports
                ports = List_Ports.comports()
                for port in ports:
                    sys.stderr.write("    %s: %s\n" %
                                     (port.device, port.description))
                sys.exit(1)

            # flush input buffer, discarding all its contents
            # pyserial 3.0+ deprecates flushInput() in favor of
            # reset_input_buffer(), but flushInput() is still present.
            self.ser.flushInput()

        elif input_file_name is not None:
            # Read from a plain file of UBX messages
            try:
                self.ser = open(input_file_name, 'rb')
            except IOError:
                sys.stderr.write('%s: failed to open input %s\n' %
                                 (self.prog_name, input_file_name))
                sys.exit(1)

    def read(self, decode_func,
             input_wait=2.0, expect_statement_identifier=None,
             raw_fd=None):
        """Read from device, until timeout or expected message.

    Arguments:
       decode_func: callable function that accepts the raw data which
                    converts it to a human readable format
       expect_statement_identifier: return only the specified package or
                                    1 if timeout. None (default) if no
                                    filtering is requested
       input_wait: read timeout in seconds. Default: 2 seconds
       raw: file descriptor like object (has to support the .write method)
            to dump raw data. None if not used
"""
        
        # are we expecting a certain message?
        if expect_statement_identifier:
            # assume failure, until we see expected message
            ret_code = 1
        else:
            # not expecting anything, so OK if we did not see it.
            ret_code = 0

        try:
            if self.gpsd_host is not None:
                # gpsd input
                start = monotonic()
                while input_wait > (monotonic() - start):
                    # First priority is to be sure the input buffer is read.
                    # This is to prevent input buffer overuns
                    if 0 < self.ser.waiting():
                        # We have serial input waiting, get it
                        # No timeout possible
                        # RTCM3 JSON can be over 4.4k long, so go big
                        new_out = self.ser.sock.recv(8192)
                        if raw_fd is not None:
                            # save to raw file
                            raw_fd.write(polybytes(new_out))
                        self.out += new_out
                    
                    consumed = decode_func(self.out)
                    # TODO: the decoder shall return a some current
                    # statement_identifier # to fill last_statement_identifier
                    last_statement_identifier = None
                    #
                    #print(consumed)
                    self.out = self.out[consumed:]
                    if ((expect_statement_identifier and
                         (expect_statement_identifier ==
                          last_statement_identifier))):
                        # Got what we were waiting for.  Done?
                        ret_code = 0

            elif self.input_is_device:
                # input is a serial device
                start = monotonic()
                while input_wait > (monotonic() - start):
                    # First priority is to be sure the input buffer is read.
                    # This is to prevent input buffer overuns
                    # pyserial 3.0+ deprecates inWaiting() in favor of
                    # in_waiting, but inWaiting() is still present.
                    if 0 < self.ser.inWaiting():
                        # We have serial input waiting, get it
                        # 1024 is comfortably large, almost always the
                        # Read timeout is what causes ser.read() to return
                        new_out = self.ser.read(1024)
                        if raw_fd is not None:
                            # save to raw file
                            raw_fd.write(polybytes(new_out))
                        self.out += new_out

                    # TODO: Code duplicated from above - make it better
                    consumed = decode_func(self.out)
                    # TODO: the decoder shall return a some current
                    # statement_identifier to fill last_statement_identifier
                    last_statement_identifier = None
                    #
                    self.out = self.out[consumed:]
                    if ((expect_statement_identifier and
                         (expect_statement_identifier ==
                          last_statement_identifier))):
                        # Got what we were waiting for.  Done?
                        ret_code = 0
            else:
                # ordinary file, so all read at once
                self.out += self.ser.read()
                if raw_fd is not None:
                    # save to raw file
                    raw_fd.write(polybytes(self.out))
                while True:
                    consumed = decode_func(self.out)
                    self.out = self.out[consumed:]
                    if 0 >= consumed:
                        break

        except IOError:
            # This happens on a good device name, but gpsd already running.
            # or if USB device unplugged
            sys.stderr.write('%s: failed to read %s\n'
                             '%s: Is gpsd already holding the port?\n'
                             % (self.prog_name, self.input_file_name,
                                self.prog_name))
            return 1

        if 0 < ret_code:
            # did not see the message we were expecting to see
            sys.stderr.write('%s: waited %0.2f seconds for, '
                             'but did not get: %%%s%%\n'
                             % (self.prog_name, input_wait,
                                expect_statement_identifier))
        return ret_code

    def write_gpsd(self, data):
        """write data to gpsd daemon."""

        # HEXDATA_MAX = 512, from gps.h, The max hex digits can write.
        # Input data is binary, converting to hex doubles its size.
        # Limit binary data to length 255, so hex data length less than 510.
        if 255 < len(data):
            sys.stderr.write('%s: trying to send %d bytes, max is 255\n'
                             % (self.prog_name, len(data)))
            return 1

        if self.gpsd_device is not None:
            # add in the requested device
            data_out = (b'?DEVICE={"path":"' +
                        polybytes(self.gpsd_device) + b'",')
        else:
            data_out = b'?DEVICE={'

        # Convert binary data to hex and build the message.
        data_out += b'"hexdata":"' + binascii.hexlify(data) + b'"}\r\n'
        if VERB_RAW <= self.verbosity_level:
            print("sent: ", data_out)
        self.ser.send(data_out)
        return 0


class gpsdata(object):
    """Position, track, velocity and status information returned by a GPS."""

    class satellite(object):
        """Class to hold satellite data."""
        def __init__(self, PRN, elevation, azimuth, ss, used=None):
            self.PRN = PRN
            self.elevation = elevation
            self.azimuth = azimuth
            self.ss = ss
            self.used = used

        def __repr__(self):
            return "PRN: %3d  E: %3d  Az: %3d  Ss: %3d  Used: %s" % (
                self.PRN, self.elevation, self.azimuth, self.ss,
                "ny"[self.used])

    def __init__(self):
        # Initialize all data members
        self.online = 0                 # NZ if GPS on, zero if not

        self.valid = 0
        self.fix = gpsfix()

        self.status = STATUS_NO_FIX
        self.utc = ""

        self.satellites_used = 0        # Satellites used in last fix
        self.xdop = self.ydop = self.vdop = self.tdop = 0
        self.pdop = self.hdop = self.gdop = 0.0

        self.epe = 0.0

        self.satellites = []            # satellite objects in view

        self.gps_id = None
        self.driver_mode = 0
        self.baudrate = 0
        self.stopbits = 0
        self.cycle = 0
        self.mincycle = 0
        self.device = None
        self.devices = []

        self.version = None

    def __repr__(self):
        st = "Time:     %s (%s)\n" % (self.utc, self.fix.time)
        st += "Lat/Lon:  %f %f\n" % (self.fix.latitude, self.fix.longitude)
        if not isfinite(self.fix.altHAE):
            st += "Altitude HAE: ?\n"
        else:
            st += "Altitude HAE: %f\n" % (self.fix.altHAE)
        if not isfinite(self.fix.speed):
            st += "Speed:    ?\n"
        else:
            st += "Speed:    %f\n" % (self.fix.speed)
        if not isfinite(self.fix.track):
            st += "Track:    ?\n"
        else:
            st += "Track:    %f\n" % (self.fix.track)
        st += "Status:   STATUS_%s\n" \
              % ("NO_FIX", "FIX", "DGPS_FIX")[self.status]
        st += "Mode:     MODE_%s\n" \
              % ("ZERO", "NO_FIX", "2D", "3D")[self.fix.mode]
        st += "Quality:  %d p=%2.2f h=%2.2f v=%2.2f t=%2.2f g=%2.2f\n" % \
              (self.satellites_used, self.pdop, self.hdop, self.vdop,
               self.tdop, self.gdop)
        st += "Y: %s satellites in view:\n" % len(self.satellites)
        for sat in self.satellites:
            st += "    %r\n" % sat
        return st


class gps(gpscommon, gpsdata, gpsjson):
    """Client interface to a running gpsd instance.

Or maybe a gpsd JSON file.
"""

    # module version, would be nice to automate the version
    __version__ = "3.22"

    def __init__(self,
                 device=None,
                 host="127.0.0.1",
                 input_file_name=None,
                 mode=0,
                 port=GPSD_PORT,
                 reconnect=False,
                 verbose=0):
        self.activated = None
        self.clock_sec = NaN
        self.clock_nsec = NaN
        self.device = device
        self.input_file_name = input_file_name
        self.path = ''
        self.precision = 0
        self.real_sec = NaN
        self.real_nsec = NaN
        self.serialmode = "8N1"
        self.verbose = verbose
        if VERB_PROG <= verbose:
            print('gps(device=%s host=%s port=%s\n'
                  '    input_file_name=%s verbose=%s)' %
                  (device, host, port, input_file_name,
                   verbose))

        gpscommon.__init__(self, host=host, port=port,
                           input_file_name=input_file_name,
                           should_reconnect=reconnect,
                           verbose=verbose)

        gpsdata.__init__(self)
        gpsjson.__init__(self)
        if mode:
            self.stream(mode)

    def _oldstyle_shim(self):
        # The rest is backwards compatibility for the old interface
        def default(k, dflt, vbit=0):
            """Return default for key."""
            if k not in self.data.keys():
                return dflt

            self.valid |= vbit
            return self.data[k]

        if self.data.get("class") == "VERSION":
            self.version = self.data
        elif self.data.get("class") == "DEVICE":
            self.valid = ONLINE_SET | DEVICE_SET
            self.path = self.data["path"]
            self.activated = default("activated", None)
            driver = default("driver", None, DEVICEID_SET)
            subtype = default("subtype", None, DEVICEID_SET)
            self.gps_id = driver
            if subtype:
                self.gps_id += " " + subtype
            self.baudrate = default("bps", 0)
            self.cycle = default("cycle", NaN)
            self.driver_mode = default("native", 0)
            self.mincycle = default("mincycle", NaN)
            self.serialmode = default("serialmode", "8N1")
        elif self.data.get("class") == "TPV":
            self.device = default("device", "missing")
            self.utc = default("time", None, TIME_SET)
            self.valid = ONLINE_SET
            if self.utc is not None:
                # self.utc is always iso 8601 string
                # just copy to fix.time
                self.fix.time = self.utc
            self.fix.altitude = default("alt", NaN, ALTITUDE_SET)  # DEPRECATED
            self.fix.altHAE = default("altHAE", NaN, ALTITUDE_SET)
            self.fix.altMSL = default("altMSL", NaN, ALTITUDE_SET)
            self.fix.climb = default("climb", NaN, CLIMB_SET)
            self.fix.epc = default("epc", NaN, CLIMBERR_SET)
            self.fix.epd = default("epd", NaN)
            self.fix.eps = default("eps", NaN, SPEEDERR_SET)
            self.fix.ept = default("ept", NaN, TIMERR_SET)
            self.fix.epv = default("epv", NaN, VERR_SET)
            self.fix.epx = default("epx", NaN, HERR_SET)
            self.fix.epy = default("epy", NaN, HERR_SET)
            self.fix.latitude = default("lat", NaN, LATLON_SET)
            self.fix.longitude = default("lon", NaN)
            self.fix.mode = default("mode", 0, MODE_SET)
            self.fix.speed = default("speed", NaN, SPEED_SET)
            self.fix.status = default("status", 1)
            self.fix.track = default("track", NaN, TRACK_SET)
        elif self.data.get("class") == "SKY":
            self.device = default("device", "missing")
            for attrp in ("g", "h", "p", "t", "v", "x", "y"):
                n = attrp + "dop"
                setattr(self, n, default(n, NaN, DOP_SET))
            if "satellites" in self.data.keys():
                self.satellites = []
                for sat in self.data['satellites']:
                    if 'el' not in sat:
                        sat['el'] = -999
                    if 'az' not in sat:
                        sat['az'] = -999
                    if 'ss' not in sat:
                        sat['ss'] = -999
                    self.satellites.append(gps.satellite(PRN=sat['PRN'],
                                           elevation=sat['el'],
                                           azimuth=sat['az'], ss=sat['ss'],
                                           used=sat['used']))
            self.satellites_used = 0
            for sat in self.satellites:
                if sat.used:
                    self.satellites_used += 1
            self.valid = ONLINE_SET | SATELLITE_SET
        elif self.data.get("class") == "PPS":
            self.device = default("device", "missing")
            self.real_sec = default("real_sec", NaN)
            self.real_nsec = default("real_nsec", NaN)
            self.clock_sec = default("clock_sec", NaN)
            self.clock_nsec = default("clock_nsec", NaN)
            self.precision = default("precision", 0)
        # elif self.data.get("class") == "DEVICES":
        # TODO: handle class DEVICES    # pylint: disable=fixme

    def read(self):
        """Read and interpret data from the daemon."""
        status = gpscommon.read(self)
        if status <= 0:
            return status
        if self.response.startswith("{") and self.response.endswith("}\r\n"):
            self.unpack(self.response)
            self._oldstyle_shim()
            self.valid |= PACKET_SET
        return 0

    def __next__(self):
        """Python 3 version of next()."""
        if self.read() == -1:
            raise StopIteration
        if hasattr(self, "data"):
            return self.data

        return self.response

    def next(self):
        """Python 2 backward compatibility."""
        return self.__next__()

    def stream(self, flags=0, devpath=None):
        """Ask gpsd to stream reports at your client."""

        gpsjson.stream(self, flags, devpath)


def is_sbas(prn):
    """Is this the NMEA ID of an SBAS satellite?."""
    return 120 <= prn <= 158


if __name__ == '__main__':
    # FIXME:  relative imports break this __main__
    description = 'gps/gps.py module.'
    usage = '%(prog)s [OPTIONS] [host [port]]'
    epilog = ('BSD terms apply: see the file COPYING in the distribution root'
              ' for details.')

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        usage=usage)
    parser.add_argument(
        '-?',
        action="help",
        help='show this help message and exit'
    )
    parser.add_argument(
        '-v',
        '--verbose',
        dest='verbose',
        default=0,
        action='count',
        help='Verbose. Repeat for more verbosity. [Default %(default)s]',
    )
    parser.add_argument(
        '-V', '--version',
        action='version',
        version="%(prog)s: Version " + gps_version + "\n",
        help='Output version to stderr, then exit'
    )
    parser.add_argument(
        'arguments',
        metavar='[host [port]]',
        nargs='*',
        help='[host [port]] Host and port to connec to gpsd on.'
    )
    options = parser.parse_args()

    streaming = False
    if len(arguments) > 2:
        sys.stderr.write("gps.py: too many positional arguments.")
        sys.exit(1)

    opts = {"verbose": options.verb}
    if options.arguments:
        opts["host"] = options.arguments[0]
        if 2 == len(options.arguments):
            opts["port"] = options.arguments[1]

    session = gps(**opts)
    session.stream(WATCH_ENABLE)
    try:
        for report in session:
            print(report)
    except KeyboardInterrupt:
        # Avoid garble on ^C
        print("")

# gps.py ends here
# vim: set expandtab shiftwidth=4
