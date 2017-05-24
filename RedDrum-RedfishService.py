# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md

# This program is dependent on the following Python packages that should be installed separately with pip:
#    pip install Flask
#
# standard python packages
import sys
import getopt
import os
import configparser

rfVersion="0.9"
rfProgram1="RedDrum-RedfishService"
rfProgram2="                "
rfUsage1="[-Vh]  [--Version][--help]"
rfUsage2="[-H<hostIP>] [-P<port>] "
rfUsage3="[--Host=<hostIP>] [--Port=<port>] "


def rfUsage():
        print("Usage:")
        print("  ",rfProgram1,"  ",rfUsage1)
        print("  ",rfProgram1,"  ",rfUsage2)
        print("  ",rfProgram2,"  ",rfUsage3)

def rfHelp():
        print("Version: ",rfVersion)
        rfUsage()
        print("")
        print("       -V,          --Version,            --- the program version")
        print("       -h,          --help,               --- help")
        print("       -H<hostIP>,  --Host=<hostIp>       --- host IP address. dflt=127.0.0.1")
        print("       -P<port>,    --Port=<port>         --- the port to use. dflt=5001")
        print("")


def main(argv):
    #set default option args
    rfHost="127.0.0.1"
    rfPort=5001
    fromMS=False

    try:
        opts, args = getopt.getopt(argv[1:],"VhLH:P:",
                        ["Version", "help", "Local", "Host=", "Port="])
    except getopt.GetoptError:
        print(rfProgram1, ":  Error parsing options")
        rfUsage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            rfHelp()
            sys.exit(0)
        elif opt in ("-V", "--Version"):
            print("Version:",rfVersion)
            sys.exit(0)
        elif opt in ("--Host="):
            rfHost=arg
        elif opt in ("--Port="):
            rfPort=int(arg)
        else:
            print("  ",rfProgram1, ":  Error: unsupported option")
            rfUsage()
            sys.exit(2)


    print("{} Version: {}".format(rfProgram1,rfVersion))
    print("   Starting RedDrum Redfish Service at:  hostIP={},  port={}".format(rfHost, rfPort))

    print("")
    print("")
    sys.stdout.flush()
    from RedDrum import redDrumMain as rdm
    rdm.redDrumMain(rdHost=rfHost,rdPort=rfPort)

if __name__ == "__main__":
    main(sys.argv)



    # Notes
    # http://127.0.0.1:5001/

    # flask api syntax
    # app.run(host="0.0.0.0") # run on all IPs
    # run(host=None, port=None, debug=None, **options)
    #   host=0.0.0.0 server avail externally -- all IPs
    #   host=127.0.0.1 is default
    #   port=5001 default, or port defined in SERVER_NAME config var



