#!/bin/bash

curl --request GET -sL \
     --url 'https://atlas.ripe.net/api/v2/probes/61020/'\
     | jq "." > one.txt

top_left_latitude="51.95" # max latitude
top_left_longitude="-3" # min longitude
bottom_right_latitude="50.95" # min latitude
bottom_right_longitude="-2" # max longitude


section_url="https://atlas.ripe.net/api/v2/probes/\
?longitude__gte=$top_left_longitude&longitude__lte=$bottom_right_longitude\
&latitude__gte=$bottom_right_latitude&latitude__lte=$top_left_latitude\
&fields=id,geometry"
echo "$section_url"
curl --request GET -sL \
     --url "$section_url"\
      | jq "." > section.txt
