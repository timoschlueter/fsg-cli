#!/usr/bin/python
"""
The MIT License (MIT)

Copyright (c) 2015 Timo Schlueter <timo.schlueter@me.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# Modules
import argparse
import urllib
import urllib2
import json
import csv
from lxml import html

# Argument parser
parser = argparse.ArgumentParser(description='Command line interface for the Fujitsu Support Gateway / AIS Connect Service')
parser.add_argument('-H', '--hostname', action="store", help='Hostname or IP address of the Fujitsu Support Gateway appliance', required = True)
parser.add_argument('-U', '--username', action="store", help='Username to login to Fujisu Support Gateway appliance', required = True)
parser.add_argument('-P', '--password', action="store", help='Password to login to Fujisu Support Gateway appliance', required = True)

subparsers = parser.add_subparsers(help='Commands', dest='command')

listParser = subparsers.add_parser('list', help='Lists all assets associated with the FSG appliance')
listParser.add_argument('-F', '--format', help='Output format for the list of assets.', choices=['raw', 'json', 'csv'], default = 'raw')

maintenanceParser = subparsers.add_parser('maintenance', help='Enable/disable maintenancen mode on specific asset')
maintenanceParser.add_argument('-A', '--asset', help='Name/Serialnumber of the asset')
maintenanceParser.add_argument('-S', '--state', help='State of maintenance mode', choices=['on', 'off'], default = 'off')

showPolicyParser = subparsers.add_parser('show', help='Shows current policy of specific asset')
showPolicyParser.add_argument('-A', '--asset', help='Name/Serialnumber of the asset')
showPolicyParser.add_argument('-F', '--format', help='Output format for the policy.', choices=['raw', 'json', 'csv'], default = 'raw')

# Coming soon - Edit poilcy
#editPolicyParser = subparsers.add_parser('edit', help='Edit the policy of specific asset')
#editPolicyParser.add_argument('-A', '--asset', help='Name/Serialnumber of the asset')
#editPolicyParser.add_argument('-O', '--options', help='The policy to set')

args = parser.parse_args()

#
# Setup
#
# Appliance URLs
fsgLoginUrl = 'https://' + args.hostname + '/html/login'
fsgAssetListUrl = 'https://' + args.hostname + '/html/AssetList.html'
fsgAssetDetailsUrl = 'https://' + args.hostname + '/html/AssetPolicy.html' #?name=CCD1914L015';
fsgPolicyEditUrl = 'https://' + args.hostname + '/html/EditPolicy'

#
# Functions
#
# Login to webinterface using username and password
def login(username, password):
    global cookie
    data = urllib.urlencode({'LoginName': username, 'Password': password, 'submit': 'Login'})
    loginReq = urllib2.urlopen(url=fsgLoginUrl, data=data)
    cookie = loginReq.headers.get('Set-Cookie')
    content = loginReq.read()

    if "AssetList.html" in content:
        return True
    else:
        print "Can't login. Please check username,password or connectivity."
        return False

# Gets the assetlist
def getAssetList(format):
    assetListReqBuilder = urllib2.build_opener()
    assetListReqBuilder.addheaders.append(('Cookie', cookie))
    assetListReq = assetListReqBuilder.open(fsgAssetListUrl)
    assetListHtml = html.fromstring(assetListReq.read())
    assetsRows = assetListHtml.xpath('//table/tbody')[0].findall('tr')

    # Generate array containing a list of asset dictionaries
    assetList = []
    for assetRow in assetsRows:
        asset = {}
        asset['SerialNumber'] = assetRow.getchildren()[0].text_content()[1:]
        asset['Type'] = assetRow.getchildren()[1].text_content()
        asset['IP'] = assetRow.getchildren()[2].text_content()
        asset['Description'] = assetRow.getchildren()[3].text_content()
        assetList.append(asset)

    # Return the assets in different formats
    if format == "json":
        print json.dumps(assetList)
    elif format == "csv":
        print "SerialNumber;Type;IP;Description"
        for currentAsset in assetList:
            print currentAsset['SerialNumber'] + ";" + currentAsset['Type'] + ";" + currentAsset['IP'] + ";" + currentAsset['Description']
    elif format == "raw":
        print "|| SerialNumber | Type | IP | Desciption ||"
        for currentAsset in assetList:
            print "| " + currentAsset['SerialNumber'] + " | " + currentAsset['Type'] + " | " + currentAsset['IP'] + " | " + currentAsset['Description'] + " |"

    return assetList

# Gets a single asset policy for specified asset
def getAssetPolicy(serialNumber, format):
    assetDetailReqBuilder = urllib2.build_opener()
    assetDetailReqBuilder.addheaders.append(('Cookie', cookie))
    assetDetailReq = assetDetailReqBuilder.open(fsgAssetDetailsUrl + '?name=' + serialNumber)
    assetDetailsHtml = html.fromstring(assetDetailReq.read())

    assetPolicyOptions = assetDetailsHtml.xpath('//select')

    assetPolicy = {}
    assetPolicy['SerialNumber'] = serialNumber

    for assetPolicyOption in assetPolicyOptions:
        assetPolicy[assetPolicyOption.name] = assetPolicyOption.value

    if format == "json":
        print json.dumps(assetPolicy)
    elif format == "csv":
        print "Policy;State"
        for assetPolicyOption in assetPolicy:
            print assetPolicyOption + ';' + assetPolicy[assetPolicyOption]
    elif format == "raw":
        print "|| Policy | State ||"
        for assetPolicyOption in assetPolicy:
            print "| " + assetPolicyOption + ' | ' + assetPolicy[assetPolicyOption] + " |"
    else:
        return assetPolicy
    return assetPolicy

# Sets a policy for specified assed
def setAssetPolicy(serialNumner, policy):
    # Not yet implemented
    print "Not yet implemented"

# Enables/disables maintenance mode for specified asset
def maintenance(serialNumber, state):
    # Get the current Policy
    currentPolicy = getAssetPolicy(serialNumber, "none")

    if state == 'on':
        servicecall = 'off'
    elif state == 'off':
        servicecall = 'on'

    # Clone the current policy...
    maintenancePolicy = currentPolicy
    # ...and modify it
    maintenancePolicy['ServiceCall'] = servicecall
    maintenancePolicy['shadowCmd'] = ''
    maintenancePolicy['connectionType'] = ''

    # Set the new policy
    setMaintenanceReqBuilder = urllib2.build_opener()
    setMaintenanceReqBuilder.addheaders.append(('Cookie', cookie))
    setMaintenanceReq = setMaintenanceReqBuilder.open(fsgPolicyEditUrl, data=urllib.urlencode(maintenancePolicy))

    # Get the new current policy and check if everything went fine
    currentPolicy = getAssetPolicy(serialNumber, "none")
    if currentPolicy['ServiceCall'] == 'on':
        print "Mainteneance mode for asset " + serialNumber + " set to OFF"
    elif currentPolicy['ServiceCall'] == 'off':
        print "Mainteneance mode for asset " + serialNumber + " set to ON"

#
# Let the Magic happen
#
# Switch through the args
if args.command == 'list':
    if login(args.username,args.password):
        getAssetList(args.format)
elif args.command == 'maintenance':
    if login(args.username,args.password):
        maintenance(args.asset, args.state)
elif args.command == 'show':
    if login(args.username,args.password):
        getAssetPolicy(args.asset, args.format)
else:
    print "Something is missing"
