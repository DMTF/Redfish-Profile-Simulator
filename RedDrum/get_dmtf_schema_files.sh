#!/bin/bash

schemas=($(curl -sL http://redfish.dmtf.org/schemas/v1/ | grep -Po '(?<=href=")[^"]*(?=")' | grep ".*\.json$"))
echo "$schemas"
for i in "${schemas[@]}"
do
    uri="http://redfish.dmtf.org/schemas/v1/$i"
    curl $uri -o RedfishService/FlaskApp/Data/DMTFSchemas/$i
done
