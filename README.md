# fsg-cli
[Fujitsu Support Gateway / AutoImmuneSystems® (AIS) Connect Service](Fujitsu Support Gateway / AIS Connect) command line interface written in Python.

This script makes it easy to interact with one or more FSG/AIS appliances without using a webbrowser.

##Requirements

* argparse
* urllib
* urllib2
* json
* csv
* lxml


## Modes

### List assets
To receive a list of registered assets, use the following command:

```bash
/usr/bin/fsg_cli.py -H ais.mydomain -U username -P password list -F json
```

The result can be either raw, json or csv.
Here the json-result:
```
[{"IP": "127.0.0.1", "SerialNumber": "ABCDEFG987654", "Type": "FSG", "Description": "Fujitsu Support Gateway - Node 0"}, {"IP": "127.0.0.2", "SerialNumber": "GFEDCBA123456", "Type": "PRIMERGY YXZ", "Description": "The best Server of all time."}]
```


### Show asset policy
To see the current policy of the asset, use the following command:
```bash
/usr/bin/fsg_cli.py -H ais.mydomain -U admin -P admin show -A GFEDCBA123456 -F json
```
The result can be either raw, json or csv.
Here the json-result:
```
{"SSHInitiate": "off", "TSHPInitiate": "off", "SerialNumber": "GFEDCBA123456", "ACAShadowInitiate": "off", "ServiceCall": "on"}
```

### Set maintenance mode


##Disclaimer
This repository is not affiliated with, funded, or in any way associated with Fujitsu Technology Solutions (FTS).
