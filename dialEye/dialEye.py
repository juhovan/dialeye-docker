#!env python
# -*- coding: iso-8859-1 -*-
###########################################################################
#
# File:            dialEye.py
#
#
# Licence:
LICENSE = """
#                  Donationware, see attached LICENSE file for more information
"""
#
#
HELP_TEXT = """
#                  See the README file.
"""
#
# Author:          Olli Lammi (olammi@iki.fi)
#
# Version:         1.0b
#
# Date:            05.03.2017
#
# Functions:       -
#
# Description:     -
#
# Requirements:    Python interpreter 2.X, 2.4 or newer (www.python.org)
#                  (tested with 2.7.8). (Series 3.X Python not supported.)
#
#                  Python Imaging Library (tested with 1.1.7)
#                  (www.pythonware.org/products/pil/)
#
# Version history: ** 24.10.2011 v0.1a (Olli Lammi) **
#                  First beta version.
#
#                  ** 30.01.2012 v0.1b (Olli Lammi) **
#                  Correction to error in shake code.
#
#                  ** 18.12.2014 v0.2a (Olli Lammi) **
#                  Developed version with easier calibration and
#                  configuration procedure.
#
#                  ** 21.12.2014 v1.0a (Olli Lammi) **
#                  Small bug fix in rotation algorithms.
#                  Released v1.0a to public.
#
#                  ** 05.03.2017 v1.0b (Olli Lammi) **
#                  Configurable needle color.
#                  Decimal result output.
#
###########################################################################

# Imports

import sys, os, os.path
import string, math
import time
import urllib.request, urllib.error, urllib.parse, base64
import tempfile

import configuration

try:
    from PIL import Image, ImageOps, ImageDraw
except:
    sys.stderr.write('ERROR: Python Imaging Library (PIL) missing.')
    sys.exit(1)

###########################################################################

# Constants

VERSION = "v1.0b"


###########################################################################

# Globals


###########################################################################

# Classes


###########################################################################

# Functions



####### main ##########################################################

def main():

  CONFIGURATION_FILE = "dialEye.conf"
  CALIBRATION_IMAGE = None

  verbose = 0
  graphics = 0
  showresult = 0
  saveshake = 0
  isurl = 0
  urluser = ''
  urlpass = ''
  disableshake = 0
  command = ''
  meterimg = ''

  # handle command line parameters
  i = 1
  while i < len(sys.argv):
      if sys.argv[i] == '--help':
          Help()
          sys.exit(1)
      elif sys.argv[i] == '-v':
          verbose = 1
      elif sys.argv[i] == '-g':
          graphics = 1
      elif sys.argv[i] == '-r':
          showresult = 1
      elif sys.argv[i] == '-s':
          saveshake = 1
      elif sys.argv[i] == '-d':
          disableshake = 1
      elif sys.argv[i] == '-u':
          isurl = 1
      elif sys.argv[i] == '--username' and i+1 < len(sys.argv):
          i = i + 1
          urluser = sys.argv[i]
      elif sys.argv[i] == '--password' and i+1 < len(sys.argv):
          i = i + 1
          urlpass = sys.argv[i]
      elif sys.argv[i] == '-m' and i+1 < len(sys.argv):
          i = i + 1
          calmethod = sys.argv[i]
      elif sys.argv[i] == '-f' and i+1 < len(sys.argv):
          i = i + 1
          CONFIGURATION_FILE = sys.argv[i]
      elif sys.argv[i] == '-c' and i+1 < len(sys.argv):
          i = i + 1
          CALIBRATION_IMAGE = sys.argv[i]
      elif len(command) <= 0 and sys.argv[i] == 'showconf':
          command = 'showconf'
      elif len(command) <= 0 and sys.argv[i] == 'meter' and i+1 < len(sys.argv):
          command = 'meter'
          i = i + 1
          meterimg = sys.argv[i]
      else:
          Usage()
          sys.exit(1)

      i = i + 1

  if len(command) <= 0:
      Usage()
      sys.exit(1)

  # load configuration file
  conf = configuration.Configuration()

  conf.addAllowedKeys(['CALIBRATION_IMAGE', 'DETECTION_TRESHOLD', \
                       'VERBOSE_LOGGING', 'GRAPHICS', 'SHOWRESULT', 'SAVESHAKE', \
                       'IMAGE_FILTER', 'DISABLE_IMAGE_SHAKE', 'SHAKE_FILE', \
                       'SHAKE_RADIUS', 'TURN_ANGLE', 'TURN_ANGLE_STEP', \
                       'ISURL', 'URLUSERNAME', 'URLPASSWORD', 'NEEDLE_COLOR', \
                       'DISABLE_ROUNDING'])
  conf.addAllowedListKeys(['DIAL', 'POSAREA'])

  (confstat, errmsg) = conf.loadFile(CONFIGURATION_FILE)
  if confstat == 0:
      print("ERROR: Cannot read configuration file: " + CONFIGURATION_FILE)
      sys.exit(1)
  elif confstat == -1:
      print("ERROR: Error reading configuration file: " + CONFIGURATION_FILE)
      print(errmsg)
      sys.exit(1)

  if CALIBRATION_IMAGE:
      conf.setValue('CALIBRATION_IMAGE', CALIBRATION_IMAGE)
  if verbose:
      conf.setValue('VERBOSE_LOGGING', 'true')
  if graphics:
      conf.setValue('GRAPHICS', 'true')
  if showresult:
      conf.setValue('SHOWRESULT', 'true')
  if saveshake:
      conf.setValue('SAVESHAKE', 'true')
  if isurl:
      conf.setValue('ISURL', 'true')
      conf.setValue('URLUSERNAME', urluser)
      conf.setValue('URLPASSWORD', urlpass)
  if disableshake:
      conf.setValue('DISABLE_IMAGE_SHAKE', 'true')

  if command == 'showconf':
      CheckCalibration(conf)
      CommandShowConfig(conf)
  elif command == 'meter':
      CheckCalibration(conf)
      CommandMeter(conf, meterimg)
  else:
      print("ERROR: Invalid command: %s" % command)


def License():
    temps = LICENSE.split('\n')
    for temp in temps:
        if len(temp) > 0 and temp[0] == '#':
            temp = temp[1:]
        if len(temp) > 0 and temp[0] == ' ':
            temp = temp[1:]
        print(temp.strip())

def Usage():
    print('USAGE:  python dialEye.py --help')
    print('        python dialEye.py [<common options>] showconf')
    print('        python dialEye.py [<common options>] [-r] [-d] [-s] [[-u] [--username <user> --password <pass>]]')
    print('                          meter <image_file or URL>')
    print('        [<common options>] = [-v] [-g] [-f <config_file>] [-c <calibration_image_file>]')
    print()
    License()

def Help():
    print("--- dialEye " + VERSION + ' ---')
    temps = HELP_TEXT.split('\n')
    for temp in temps:
        if len(temp) > 0 and temp[0] == '#':
            temp = temp[1:]
        if len(temp) > 0 and temp[0] == ' ':
            temp = temp[1:]
        print(temp)

    License()

def InsertVersion(img, color):
    d = ImageDraw.Draw(img)
    ts = d.textsize('dialEye ' + VERSION)
    d.text((img.size[0] - ts[0] - 1, img.size[1] - ts[1] - 1), 'dialEye ' + VERSION, fill=color)
    del d


def CheckCalibration(conf):
    calfile = GetCalibrationName(conf)
    if not os.path.exists(calfile):
        print("ERROR: Calibration image not accessible: %s" % calfile)
        print("       Reconfigure dialEye.")
        sys.exit(1)

def GetCalibrationName(conf):
    calfile = conf.getValue('CALIBRATION_IMAGE', '')
    if len(calfile) > 0:
        return calfile
    return 'dialeye_calibration_image.png'

def LoadCalibrationImage(conf):
    tmpimg = None
    calfile = GetCalibrationName(conf)
    try:
        tmpimg = Image.open(calfile)
        tmpimg.load()
    except:
        return None

    return tmpimg

def GetDials(conf):
    confdials = conf.getValue('DIAL', [])
    dials = []
    for cd in confdials:
        cdl = cd.split(':')
        if len(cdl) == 8 or len(cdl) == 11:
            try:
                cx = int(cdl[0].strip())
                cy = int(cdl[1].strip())
                mrad = float(cdl[2].strip())
                irad = float(cdl[3].strip())
                dangle = float(cdl[4].strip())
                dangle2 = float(cdl[5].strip())
                za = float(cdl[6].strip())
                rd = int(cdl[7].strip())
                needle_color = None
                if len(cdl) == 11:
                    r = int(cdl[8].strip())
                    g = int(cdl[9].strip())
                    b = int(cdl[10].strip())
                    needle_color = (r, g, b)
                dials.append({'cx': cx, 'cy': cy, 'meter_radius': mrad, \
                              'inner_radius': irad, 'dial_angle': dangle, \
                              'dial_angle2': dangle2, 'zero_angle': za, \
                              'rot_direction': rd, 'needle_color': needle_color})
            except:
                print("ERROR: Invalid DIAL config: %s" % cd)
        else:
            print("ERROR: Invalid DIAL config: %s" % cd)

    return dials

def GetPosareas(conf):
    confposareas = conf.getValue('POSAREA', [])
    posareas = []
    for cd in confposareas:
        cdl = cd.split(':')
        if len(cdl) == 4:
            try:
                x1 = int(cdl[0].strip())
                y1 = int(cdl[1].strip())
                x2 = int(cdl[2].strip())
                y2 = int(cdl[3].strip())
                posareas.append([min(x1,x2), min(y1,y2), max(x1,x2), max(y1,y2)])
            except:
                print("ERROR: Invalid POSAREA config: %s" % cd)
        else:
            print("ERROR: Invalid POSAREA config: %s" % cd)

    return posareas

def GetShakes(conf):
    confshakes = conf.getValue('SHAKE', [])
    shakes = []
    for cs in confshakes:
        csl = cs.split(':')
        if len(csl) == 3:
            try:
                dx = int(csl[0].strip())
                dy = int(csl[1].strip())
                rangle = float(csl[2].strip())
                shakes.append([dx, dy, rangle])
            except:
                print("ERROR: Invalid SHAKE config: %s" % cs)
        else:
            print("ERROR: Invalid SHAKE config: %s" % cs)

    return shakes

def GetShakeFileName(conf):
    return conf.getValue('SHAKE_FILE', 'dialeye_shakes.conf')

def SaveShakes(fname, shakes):
    try:
        outf = open(fname, 'w')
    except:
        return False

    try:
        for s in shakes:
            outf.write('@SHAKE=%d:%d:%.2f\n' % (s[0], s[1], s[2]))
    except:
        try:
            outf.close()
        except:
            pass
        return False

    try:
        outf.close()
    except:
        return False

    return True

def CheckDials(imgsz, dials):
    for dial in dials:
        if dial['meter_radius'] < dial['inner_radius']:
            print("ERROR: Dial inner radius bigger than meter radius.")
            sys.exit(1)

        if dial['cx'] + dial['meter_radius'] > imgsz[0]-1 \
            or dial['cx'] + dial['meter_radius'] < 0 \
            or dial['cy'] + dial['meter_radius'] > imgsz[1]-1 \
            or dial['cy'] + dial['meter_radius'] < 0:
            print("ERROR: Dial meter circle is out of image boundaries.")
            sys.exit(1)

        if dial['rot_direction'] != 0 and dial['rot_direction'] != 1:
            print("ERROR: Dial direction of rotation invalid.")
            sys.exit(1)

def CheckPosareas(imgsz, posareas):
    for area in posareas:
        if area[0] > imgsz[0]-1 \
            or area[0] < 0 \
            or area[1] > imgsz[1]-1 \
            or area[1] < 0 \
            or area[2] > imgsz[0]-1 \
            or area[2] < 0 \
            or area[3] > imgsz[1]-1 \
            or area[3] < 0:
            print("ERROR: Posarea is out of image boundaries. (%d, %d, %d, %d)" % (area[0], area[1], area[2], area[3]))
            sys.exit(1)

def CommandShowConfig(conf):
    calimg = LoadCalibrationImage(conf)

    if not calimg:
        print("ERROR: Cannot load calibration image: %s" % GetCalibrationName(conf))
        sys.exit(1)

    calimg = calimg.convert('L')
    calimg = calimg.convert('RGB')

    dials = GetDials(conf)
    CheckDials(calimg.size, dials)
    for dial in dials:
        ShowParams(calimg, dial, 0.0)
    posareas = GetPosareas(conf)
    CheckPosareas(calimg.size, posareas)
    for area in posareas:
        ShowParamsPosarea(calimg, area)
    InsertVersion(calimg, (127,127,127))

    if conf.isTrue('GRAPHICS'):
        calimg.show()
    else:
        print("Writing dialeye_conf.png")
        calimg.save('dialeye_conf.png')

def ShowParams(img, dial, value, nodirection = 0, nodialangle = 0, sdata = [0,0,0.0]):
    data = list(img.getdata())

    mrad = dial['meter_radius']
    irad = dial['inner_radius']
    dangle = dial['dial_angle']
    dangle2 = dial['dial_angle2']
    drot = dial['rot_direction']

    (dcpx, dcpy) = ShakeMovePoint(img.size, (dial['cx'], dial['cy']), sdata)

    val = value
    if drot == 1:
        val = 10 - value
    angle = (val / 10.0 * 360.0 + dial['zero_angle'] + sdata[2]) % 360.0
    sinza = math.sin( math.radians(angle) )
    cosza = math.cos( math.radians(angle) )

    f = 0.0
    while f < 1.0:
        dx = int(round(f * mrad * sinza))
        dy = int(round(-f * mrad * cosza))
        pos = (dcpy+dy) * img.size[0] + dcpx+dx
        data[pos] = (0,255,0)
        f = f + 1.0 / mrad

    sinan = math.sin(math.radians(dangle/2.0))
    cosan = math.cos(math.radians(dangle/2.0))
    sinan2 = math.sin(math.radians(dangle2/2.0))
    cosan2 = math.cos(math.radians(dangle2/2.0))

    if not nodialangle:
        p1x = mrad * sinan
        p1y = -mrad * cosan
        p2x = irad * sinan2
        p2y = -irad * cosan2

        if dangle < 0:
            p1y = p1y - p1x * (p1y - p2y) / (p1x - p2x)
            p1x = 0

        if dangle2 < 0:
            p2y = p2y - p2x * (p1y - p2y) / (p1x - p2x)
            p2x = 0

        p3x = -p1x
        p3y = p1y
        p4x = -p2x
        p4y = p2y

        p1 = RotatePoint((p1x, p1y), angle)
        p2 = RotatePoint((p2x, p2y), angle)
        p3 = RotatePoint((p3x, p3y), angle)
        p4 = RotatePoint((p4x, p4y), angle)

        line1 = GetLinePoints(p2, p1)
        line2 = GetLinePoints(p4, p3)

        for p in line1 + line2:
            dx = int(round(p[0]))
            dy = int(round(p[1]))
            pos = (dcpy+dy) * img.size[0] + dcpx+dx
            data[pos] = (255,0,0)

    if not nodirection:
        a = 20.0
        if drot == 1:
            a = -a
        dx = mrad * sinza
        dy = -mrad * cosza
        sinap = math.sin(math.radians(a))
        cosap = math.cos(math.radians(a))
        ndx = dx * cosap - dy * sinap
        ndy = dy * cosap + dx * sinap
        na = angle + a + 90.0
        if drot == 1:
            na = na - 180.0
        sinnu = math.sin(math.radians((na - 135.0) % 360.0))
        cosnu = math.cos(math.radians((na - 135.0) % 360.0))
        sinnu2 = math.sin(math.radians((na + 135.0) % 360.0))
        cosnu2 = math.cos(math.radians((na + 135.0) % 360.0))

        f = 0.0
        while f < 1.0:
            dx = f * 10.0 * sinnu
            dy = -f * 10.0 * cosnu
            nx = int(round(ndx + dx))
            ny = int(round(ndy + dy))
            pos = (dcpy+ny) * img.size[0] + dcpx+nx
            data[pos] = (0,255,0)
            dx = f * 10.0 * sinnu2
            dy = -f * 10.0 * cosnu2
            nx = int(round(ndx + dx))
            ny = int(round(ndy + dy))
            pos = (dcpy+ny) * img.size[0] + dcpx+nx
            data[pos] = (0,255,0)
            f = f + 1.0 / 10.0

    for a in range(0,360):
        sina = math.sin( math.radians(a) )
        cosa = math.cos( math.radians(a) )

        dx = int(round(mrad * sina))
        dy = int(round(-mrad * cosa))
        pos = (dcpy+dy) * img.size[0] + dcpx+dx
        data[pos] = (0,255,0)

        dx = int(round(irad * sina))
        dy = int(round(-irad * cosa))
        pos = (dcpy+dy) * img.size[0] + dcpx+dx
        data[pos] = (0,0,255)

    img.putdata(data)


def ShowParamsPosarea(img, area):
    areacolor = (255,255,0)
    data = list(img.getdata())

    for x in range(area[0], area[2]+1):
        pos = area[1] * img.size[0] + x
        data[pos] = areacolor
        pos = area[3] * img.size[0] + x
        data[pos] = areacolor
    for y in range(area[1]+1, area[3]):
        pos = y * img.size[0] + area[0]
        data[pos] = areacolor
        pos = y * img.size[0] + area[2]
        data[pos] = areacolor

    img.putdata(data)


def GetPointAngle(p):
    r = GetPointRadius(p)
    if p[0] >= 0.0:
        if p[1] < 0.0:
            return math.degrees(math.asin(p[0]/r))
        else:
            return 90.0 + math.degrees(math.asin(p[1]/r))
    else:
        if p[1] < 0.0:
            return 270.0 + math.degrees(math.asin(-p[1]/r))
        else:
            return 180.0 + math.degrees(math.asin(-p[0]/r))

def GetPointRadius(p):
    return math.sqrt(p[0]*p[0] + p[1]*p[1])

def RotatePoint(p, angle, si = None, co = None):
    if si == None:
        si = math.sin( math.radians(angle) )
    if co == None:
        co = math.cos( math.radians(angle) )
    nx = p[0] * co - p[1] * si
    ny = p[1] * co + p[0] * si
    return (nx, ny)

def RotatePoints(ps, angle, si = None, co = None):
    if si == None:
        si = math.sin( math.radians(angle) )
    if co == None:
        co = math.cos( math.radians(angle) )
    points = []
    for p in ps:
        nx = p[0] * co - p[1] * si
        ny = p[1] * co + p[0] * si
        points.append((nx, ny))
    return points

def GetImageURL(url, username = None, passwd = None):
    res = ''
    try:
        req = urllib.request.Request(url)
        if username != None and len(username) > 0:
            req.add_header('Authorization', bytes('Basic ','utf-8') + base64.b64encode(bytes(username + ':' + passwd,'utf-8')))
        f = urllib.request.urlopen(req)
        res = f.read()
        f.close()
    except Exception as e:
        print("ERROR: " + e.__str__())
        return None

    tempfname = ''
    try:
        (tempfd, tempfname) = tempfile.mkstemp()
        os.close(tempfd)
    except:
        print('ERROR: Cannot create temporary file for image')
        return None

    try:
        f = open(tempfname,'wb')
        f.write(res)
        f.close()
    except:
        print("ERROR: Cannot write temporary image file: " + tempfname)
        return None

    tempimg = GetImageFile(tempfname)
    os.unlink(tempfname)
    return tempimg

def GetImageFile(fname):
    tempimg = None
    try:
        tempimg = Image.open(fname)
        tempimg.load()
    except:
        return None
    return tempimg

def CommandMeter(conf, meterfile):
    resimg = None
    resdata = None

    if conf.isTrue('ISURL'):
        username = conf.getValue('URLUSERNAME', '')
        password = conf.getValue('URLPASSWORD', '')
        meterimg = GetImageURL(meterfile, username, password)
        if meterimg == None:
            print("ERROR: Cannot load meter image from URL: %s" % meterfile)
            sys.exit(1)
    else:
        meterimg = GetImageFile(meterfile)
        if not meterimg:
            print("ERROR: Cannot load meter image file: %s" % meterfile)
            sys.exit(1)

    meterimg = meterimg.convert('RGB')
    meterdata = list(meterimg.getdata())

    if conf.isTrue('SHOWRESULT'):
        resimg = Image.new('RGB', meterimg.size)
        resimg.putdata(meterdata)
        resimg = resimg.convert('L')
        resimg = resimg.convert('RGB')
        resdata = list(resimg.getdata())

    dials = GetDials(conf)
    CheckDials(meterimg.size, dials)

    posareas = GetPosareas(conf)

    shakeconf = configuration.Configuration()
    shakeconf.addAllowedListKeys(['SHAKE'])

    shakefile = GetShakeFileName(conf)
    if os.path.exists(shakefile):
        if conf.isTrue('VERBOSE_LOGGING'):
            print("Loading shake configuration from " + shakefile)

        (confstat, errmsg) = shakeconf.loadFile(shakefile)
        if confstat == 0:
            print("ERROR: Cannot read shake configuration file: " + shakefile)
            sys.exit(1)
        elif confstat == -1:
            print("ERROR: Error reading configuration file: " + shakefile)
            print(errmsg)
            sys.exit(1)

    shakes = GetShakes(shakeconf)
    if len(shakes) > 0 and len(shakes) != 1:
        print("ERROR: Invalid SHAKE configuration. Using only first SHAKE row.")
        shakes = [shakes[0]]

    if conf.isTrue('VERBOSE_LOGGING'):
        print()
        print("Preloaded shakes:")
        for s in shakes:
            print("  dx = %d, dy = %d, rotation = %.2f degrees" % (s[0], s[1], s[2]))

        print()
        if not conf.isTrue('DISABLE_IMAGE_SHAKE'):
            print("Shaking and metering...")
        else:
            print("Metering...")

    shaketime = 0
    metertime = 0
    values = []
    shakeresults = []
    sdata = [0, 0, 0.0]
    if len(shakes) > 0:
        sdata = shakes[0]

    if not conf.isTrue('DISABLE_IMAGE_SHAKE') and len(posareas) > 0:
        tt = time.time()

        calimg = LoadCalibrationImage(conf)
        CheckPosareas(calimg.size, posareas)

        tempmeterimg = Image.new('RGB', meterimg.size)
        tempmeterimg.putdata(meterdata)
        tempmeterimg = tempmeterimg.convert('L')
        tempmeterdata = list(tempmeterimg.getdata())

        if not calimg:
            print("ERROR: Cannot load calibration image: %s" % GetCalibrationName(conf))
            sys.exit(1)

        if calimg.size != meterimg.size:
            print("ERROR: Calibration image and meter image sizes are not equal.")
            sys.exit(1)

        calimg = calimg.convert('L')
        caldata = list(calimg.getdata())

        sdata = SearchPosareas(conf, sdata, calimg.size, caldata, tempmeterdata, posareas)
        shaketime = shaketime + (time.time() - tt)
    shakeresults.append(sdata)

    # if filtering is enabled
    filtername = conf.getValue('IMAGE_FILTER', 'NONE').upper()
    if filtername and filtername != 'NONE':
        tt = time.time()
        meterdata = DoImageFiltering(meterimg.size, meterdata, dials, sdata, filtername)
        metertime = metertime + (time.time() - tt)

    for i in range(len(dials)):
        dial = dials[i]
        tt = time.time()
        values.append(ReadMeter(conf, meterimg.size, meterdata, dial, sdata, resdata))
        metertime = metertime + (time.time() - tt)

    if conf.isTrue('SAVESHAKE'):
        SaveShakes(shakefile, shakeresults)
        if conf.isTrue('VERBOSE_LOGGING'):
            print()
            print("Saved shake configuration to " + shakefile)

    if conf.isTrue('SHOWRESULT'):
        resimg.putdata(resdata)

        for i in range(len(dials)):
            ShowParams(resimg, dials[i], values[i], 1, 1, sdata)

        InsertVersion(resimg, (127,127,127))

        if conf.isTrue('GRAPHICS'):
            resimg.show()
        else:
            print()
            print("Writing dialeye_result.png")
            resimg.save('dialeye_result.png')

    finstr = CalcCounterValue(conf, values)

    if conf.isTrue('VERBOSE_LOGGING'):
        print()
        print("Times: shaking: %.2f sec,  metering: %.2f sec" % (shaketime, metertime))
        print()

        if not conf.isTrue('DISABLE_IMAGE_SHAKE'):
            print("Calculated shakes:")
            for s in shakeresults:
                print("  dx = %d, dy = %d, rotation = %.2f degrees" % (s[0], s[1], s[2]))
            print()

        print("Measured meter dial values:")
        for value in values:
            print("  %.2f" % value)
        print()
        print("Result:")

    print(finstr)


def GetCirclePoints(inner_radius, outer_radius):
    mrad = int(round(outer_radius))
    irad = int(round(inner_radius))
    points = []
    for dx in range(-mrad, mrad+1):
        for dy in range(-mrad, mrad+1):
            d = math.sqrt(dx*dx + dy*dy)
            if d <= mrad and d >= irad:
                points.append((dx, dy))
    return points

def GetLinePoints(p1, p2):
    points = []
    dex = p2[0]-p1[0]
    dey = p2[1]-p1[1]
    l = math.sqrt(dex*dex + dey*dey)
    f = 0.0
    while f <= 1.0:
        dx = f * dex
        dy = f * dey
        points.append( (p1[0] + dx, p1[1] + dy) )
        f = f + 1.0 / l
    return points

def GetAvgColor(sz, data, cp):
    points = [[-1,-1], [0,-1], [1,-1], [-1,0], [0,0], [1,0], [-1,1], [0,1], [1,1]]
    res = [0, 0, 0]
    for p in points:
        pos = (cp[1] + p[1]) * sz[0] + cp[0] + p[0]
        c = data[pos]
        res[0] = res[0] + c[0]
        res[1] = res[1] + c[1]
        res[2] = res[2] + c[2]
    res[0] = int(round(res[0] / 9.0))
    res[1] = int(round(res[1] / 9.0))
    res[2] = int(round(res[2] / 9.0))
    return (res[0], res[1], res[2])

def GetDialPoints(dial):
    mrad = dial['meter_radius']
    irad = dial['inner_radius']
    dangle = dial['dial_angle']
    dangle2 = dial['dial_angle2']

    sinan = math.sin(math.radians(dangle/2.0))
    cosan = math.cos(math.radians(dangle/2.0))
    sinan2 = math.sin(math.radians(dangle2/2.0))
    cosan2 = math.cos(math.radians(dangle2/2.0))

    p1x = mrad * sinan
    p1y = -mrad * cosan
    p2x = irad * sinan2
    p2y = -irad * cosan2

    if dangle < 0:
        p1y = p1y - p1x * (p1y - p2y) / (p1x - p2x)
        p1x = 0

    if dangle2 < 0:
        p2y = p2y - p2x * (p1y - p2y) / (p1x - p2x)
        p2x = 0

    points = []
    cp = GetCirclePoints(irad, mrad)
    for p in cp:
        r = GetPointRadius(p)
        r1 = GetPointRadius((p1x, p1y))
        r2 = GetPointRadius((p2x, p2y))
        if r >= r2 and r <= r1:
            a = (p2y - p1y) / (p2x - p1x)
            b = p1y - a * p1x
            temp = math.sqrt(4*a*a*b*b-4*(a*a+1)*(b*b-r*r))
            mx1 = (temp - 2 * a * b) / (2 * (a*a + 1))
            mx2 = (-temp - 2 * a * b) / (2 * (a*a + 1))
            my1 = a * mx1 + b
            my2 = a * mx2 + b
            f1 = (mx1 - p1x) / (p2x - p1x)
            f2 = (mx2 - p1x) / (p2x - p1x)
            if f1 >= 0.0 and f1 <= 1.0:
                mp = (mx1, my1)
            elif f2 >= 0.0 and f2 <= 1.0:
                mp = (mx2, my2)
            else:
                continue
            a = GetPointAngle(mp)
            pa = GetPointAngle(p)
            if pa > 180.0:
                pa = pa - 360.0
            if abs(pa) <= a:
                points.append(p)

    return points

def CalculatePoint(x, y, imgdata, sz):
    ix = math.floor(x)
    iy = math.floor(y)
    dx = x - ix
    dy = y - iy
    ix = int(ix)
    iy = int(iy)
    ixp = ix+1
    iyp = iy+1
    if ixp > sz[0]-1:
        ixp = ix
    if iyp > sz[1]-1:
        iyp = iy

    p1 = imgdata[iy * sz[0] + ix]
    p2 = imgdata[iy * sz[0] + ixp]
    p3 = imgdata[iyp * sz[0] + ix]
    p4 = imgdata[iyp * sz[0] + ixp]

    dp1 = 1.0 - math.sqrt(dx*dx + dy*dy)
    dp2 = 1.0 - math.sqrt((1.0 - dx)*(1.0 - dx) + dy*dy)
    dp3 = 1.0 - math.sqrt(dx*dx + (1.0 - dy)*(1.0 - dy))
    dp4 = 1.0 - math.sqrt((1.0 - dx)*(1.0 - dx) + (1.0 - dy)*(1.0 - dy))
    if dp1 < 0.0:
        dp1 = 0.0
    if dp2 < 0.0:
        dp2 = 0.0
    if dp3 < 0.0:
        dp3 = 0.0
    if dp4 < 0.0:
        dp4 = 0.0

    return (dp1 * p1 + dp2 * p2 + dp3 * p3 + dp4 * p4) / (dp1 + dp2 + dp3 + dp4)


def GetPosareaPoints(area, justCorners = False):
    result = []
    if justCorners:
        result.append((area[0], area[1]))
        result.append((area[0], area[3]))
        result.append((area[2], area[1]))
        result.append((area[2], area[3]))
    else:
        for x in range(area[0], area[2] + 1):
            for y in range(area[1], area[3] + 1):
                result.append((x,y))
    return result


def SearchPosareas(conf, sdata, sz, caldata, meterdata, posareas):
    SHAKE_RADIUS = int(conf.getValue('SHAKE_RADIUS', '7'))
    TURN_ANGLE = float(conf.getValue('TURN_ANGLE', '5.0'))
    TURN_ANGLE_STEP = float(conf.getValue('TURN_ANGLE_STEP', '0.5'))

    sx = sdata[0]
    sy = sdata[1]
    sa = sdata[2]

    startx = starty = -SHAKE_RADIUS
    endx = endy = SHAKE_RADIUS

    points = [(0,0)]
    for r in range(1, SHAKE_RADIUS + 1):
        for x in [-r, r]:
            for y in range(-r, r+1):
                if x >= startx and x <= endx and y >= starty and y <= endy:
                    points.append((x,y))
        for y in [-r, r]:
            for x in range(-r+1, r):
                if x >= startx and x <= endx and y >= starty and y <= endy:
                    points.append((x,y))

    angles = [0.0]
    a = TURN_ANGLE_STEP
    while a <= TURN_ANGLE:
        angles.append((-a) % 360.0)
        angles.append(a)
        a = a + TURN_ANGLE_STEP

    score = None
    scorex = sx
    scorey = sy
    scorea = (sa % 360.0)

    apoints = []
    for area in posareas:
        temp_cornerapoints = GetPosareaPoints(area, True)

        isoutofbounds = False
        for (dx, dy) in temp_cornerapoints:
            for turna in angles:
                sina = math.sin(math.radians(turna+scorea))
                cosa = math.cos(math.radians(turna+scorea))
                for (x,y) in points:
                    tx = dx - ((sz[0]-1) / 2.0)
                    ty = dy - sz[1]-1
                    ntx = tx * cosa - ty * sina
                    nty = ty * cosa + tx * sina
                    ndx = ntx + ((sz[0]-1) / 2.0) - dx
                    ndy = nty + sz[1]-1 - dy

                    if dx < 0 or dx >= sz[0] or dx+sx+x+ndx < 0 or dx+sx+x+ndx >= sz[0] or \
                        dy < 0 or dy >= sz[1] or dy+sy+y+ndy < 0 or dy+sy+y+ndy >= sz[1]:
                        isoutofbounds = True
                        break
                if isoutofbounds:
                    break
            if isoutofbounds:
                break

        if not isoutofbounds:
            apoints = apoints + GetPosareaPoints(area)
        else:
            for (dx, dy) in GetPosareaPoints(area):
                incl = True
                for turna in angles:
                    sina = math.sin(math.radians(turna+scorea))
                    cosa = math.cos(math.radians(turna+scorea))
                    for (x,y) in points:
                        tx = dx - ((sz[0]-1) / 2.0)
                        ty = dy - sz[1]-1
                        ntx = tx * cosa - ty * sina
                        nty = ty * cosa + tx * sina
                        ndx = ntx + ((sz[0]-1) / 2.0) - dx
                        ndy = nty + sz[1]+1 - dy

                        if dx < 0 or dx >= sz[0] or dx+sx+x+ndx < 0 or dx+sx+x+ndx >= sz[0] or \
                            dy < 0 or dy >= sz[1] or dy+sy+y+ndy < 0 or dy+sy+y+ndy >= sz[1]:
                            incl = False
                            break
                    if not incl:
                        break
                if incl:
                    apoints.append((dx, dy))

    for turna in angles:
        sina = math.sin(math.radians(turna+sa))
        cosa = math.cos(math.radians(turna+sa))
        for (x,y) in points:
            tempscore = 0
            for (dx, dy) in apoints:
                tx = dx - ((sz[0]-1) / 2.0)
                ty = dy - sz[1]-1
                ntx = tx * cosa - ty * sina
                nty = ty * cosa + tx * sina
                ndx = ntx + ((sz[0]-1) / 2.0) - dx
                ndy = nty + sz[1]+1 - dy

                calp = caldata[dy * sz[0] + dx]
                metp = CalculatePoint(dx+sx+x+ndx, dy+sy+y+ndy, meterdata, sz)
                tempscore = tempscore + abs(calp - metp)
                if score != None and tempscore > score:
                    break

            if score == None or tempscore < score:
                score = tempscore
                scorex = x + sx
                scorey = y + sy
                scorea = (turna + sa) % 360.0

    return [scorex, scorey, scorea]


def ShakeMovePoint(sz, point, sdata):
    dcptemp = (point[0] - ((sz[0]-1) / 2.0), point[1] - sz[1]-1)
    dcptemp = RotatePoint(dcptemp, sdata[2])
    dcpx = int(round(dcptemp[0] + ((sz[0]-1) / 2.0) + sdata[0]))
    dcpy = int(round(dcptemp[1] + sz[1]+1 + sdata[1]))
    return (dcpx, dcpy)


def ReadMeter(conf, sz, meterdata, dial, sdata, resdata):
    treshold = int(conf.getValue('DETECTION_TRESHOLD', '20')) / 100.0

    mrad = dial['meter_radius']
    irad = dial['inner_radius']
    dialangle = dial['dial_angle']

    # calculate new dial center (x and y pan plus rotation)
    (dcpx, dcpy) = ShakeMovePoint(sz, (dial['cx'], dial['cy']), sdata)

    temps = 2 * int(math.ceil(mrad)) + 1
    cx = cy = (temps - 1) / 2
    csz = (temps, temps)
    cdata = list(Image.new('L', csz, 0).getdata())

    dialcolor = dial['needle_color']
    if dialcolor == None:
        dialcolor = GetAvgColor(sz, meterdata, (dcpx, dcpy))

    if conf.isTrue('VERBOSE_LOGGING'):
        print()
        print("Dial color (RGB): %d,%d,%d" % dialcolor)
        print()

    cpoints = GetCirclePoints(irad, mrad)
    cmax = None
    cmin = None
    for p in cpoints:
        pos = (dcpy + p[1]) * sz[0] + dcpx + p[0]
        origcolor = meterdata[pos]
        a = dialcolor[0] - origcolor[0]
        b = dialcolor[1] - origcolor[1]
        c = dialcolor[2] - origcolor[2]
        val = math.sqrt(a*a + b*b + c*c)
        if cmax == None or cmax < val:
            cmax = val
        if cmin == None or cmin > val:
            cmin = val
        pos = int((cy + p[1]) * csz[0] + cx + p[0])
        cdata[pos] = val

    for p in cpoints:
        pos = int((cy + p[1]) * csz[0] + cx + p[0])
        if cdata[pos] > (cmax * treshold):
            cdata[pos] = 0
        else:
            cdata[pos] = 255 - int(round(255.0 / (cmax*treshold-cmin) * (cdata[pos] - cmin)))

    dialpoints = GetDialPoints(dial)


    anglevalues = 360 * [0]
    maxval = 0

    for angle in range(0,360,10):
        rdialpoints = RotatePoints(dialpoints, angle, None, None)
        angval = 0
        for p in rdialpoints:
            pos = int(round(cy + p[1])) * csz[0] + int(round(cx + p[0]))
            angval = angval + cdata[pos]

        if angval > maxval:
            maxval = angval
        anglevalues[angle] = angval

    dialangles = []
    for angle in range(0,360,10):
        if anglevalues[angle] > 0.5 * maxval:
            for a in range(angle-5, angle+5):
                if a != angle:
                    dialangles.append(a % 360)

    for angle in dialangles:
        rdialpoints = RotatePoints(dialpoints, angle, None, None)
        angval = 0
        for p in rdialpoints:
            pos = int(round(cy + p[1])) * csz[0] + int(round(cx + p[0]))
            angval = angval + cdata[pos]

        anglevalues[angle] = angval

    maxscore = -1
    maxscoreangles = []
    for angle in range(0,360):
        score = anglevalues[angle]
        if score > maxscore:
            maxscore = score
            maxscoreangles = [angle]
        elif score == maxscore:
            maxscoreangles.append(angle)

    if resdata != None:
        prev = None
        for angle in range(0,361):
            sina = math.sin( math.radians(angle) )
            cosa = math.cos( math.radians(angle) )
            if (maxscore <= 0):
                continue
            r = (float(anglevalues[angle % 360]) / float(maxscore)) * (mrad-irad) + irad
            dx = r * sina
            dy = -r * cosa

            point = (dcpx+dx, dcpy+dy)
            if prev != None:
                lpoints = GetLinePoints(prev, point)
                for p in lpoints:
                    pos = int(round(p[1])) * sz[0] + int(round(p[0]))
                    resdata[pos] = (255,0,0)
            prev = point

    if len(maxscoreangles) > 0:
        maxa = max(maxscoreangles)
        for i in range(len(maxscoreangles)):
            if maxa - maxscoreangles[i] > 180:
                maxscoreangles[i] = maxscoreangles[i] + 360
    else:
        print("ERROR: Nothing detected in dial area. Check treshold configuration.")
        sys.exit(1)

    kulma = (float(sum(maxscoreangles))/len(maxscoreangles) - dial['zero_angle'] - sdata[2]) % 360.0
    arvo =  kulma / 360.0 * 10.0

    if dial['rot_direction'] == 1:
        arvo = 10.0 - arvo

    return arvo


def CalcCounterValue(conf, arvot):
    finstr = ''
    prevval = 0
    for i in range(len(arvot)):
            arvo = arvot[len(arvot)-1-i]
            if i == 0:
                if conf.isTrue('DISABLE_ROUNDING'):
                    prevval = math.floor(arvo) % 10
                    finstr = '%.2f' % arvo
                else:
                    prevval = round(arvo) % 10
                    finstr = '%d' % prevval
            else:
                korjaus = 0
                if prevval < 5 and (arvo - math.floor(arvo)) * 10.0 - prevval > 5:
                    korjaus = 1
                if prevval > 5 and prevval - (arvo - math.floor(arvo)) * 10.0 > 5:
                    korjaus = -1
                prevval = math.floor(arvo + korjaus) % 10
                finstr = '%d' % prevval + finstr

    return finstr


def DoImageFiltering(sz, data, dials, sdata, filtername):
    if filtername == 'NONE':
        return data
    elif filtername in ['RED', 'BLUE', 'GREEN']:
        filterpoints = []
        for dial in dials:
            mrad = dial['meter_radius']
            # calculate new dial center (x and y pan plus rotation)
            (dcpx, dcpy) = ShakeMovePoint(sz, (dial['cx'], dial['cy']), sdata)
            for p in GetCirclePoints(0, mrad):
                filterpoints.append((dcpx + p[0], dcpy + p[1]))

        tmin = None
        tmax = None
        for (x, y) in filterpoints:
            pos = (y * sz[0]) + x
            val = data[pos]

            if filtername == 'RED':
                cval = val[0] - (val[1] + val[2]) / 2.0
            elif filtername == 'GREEN':
                cval = val[1] - (val[0] + val[2]) / 2.0
            elif filtername == 'BLUE':
                cval = val[2] - (val[0] + val[1]) / 2.0

            if tmin == None or tmin > cval:
                tmin = cval
            if tmax == None or tmax < cval:
                tmax = cval
            data[pos] = cval
        for (x, y) in filterpoints:
            pos = (y * sz[0]) + x
            val = int(round(255.0 / (tmax-tmin) * (data[pos] - tmin)))
            data[pos] = (val, val, val)
        return data
    else:
        print("ERROR: Unknown image filter: %s" % filtername)
        sys.exit(1)


###########################################################################

if __name__ == "__main__":
  main()


