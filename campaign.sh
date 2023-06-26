#!/bin/bash

###############################################################################
# Constants
campaign_name="WW_validation_20230620"
probes_sets_path="datasets/probes_sets/"
probes_sets_names_list=(
"WW_100.json"
"WW_300.json"
"WW_500.json"
"WW_1000.json"
#"WW-section_1.5.json"
#"WW-section_1.json"
#"WW-section_2.json"
)
target_direction_list=(
"198.41.0.4" "199.9.14.201" "192.33.4.12" "199.7.91.13" "192.203.230.10"
"192.5.5.241" "192.112.36.4" "198.97.190.53" "192.36.148.17" "192.58.128.30"
"193.0.14.129" "199.7.83.42" "202.12.27.33" "104.16.123.96")

do_measurement_campaign_to_target()
{
  ip=$1
  campaign_selected=$2
  for probes_filepath in "${probes_sets_names_list[@]}"; do
    # echo the command used
    echo ./igreedy.sh -m "$ip" \
    -p "$probes_sets_path$probes_filepath" \
    -c "$campaign_selected"
    echo ""
    # Start the measurement
    ./igreedy.sh -m "$ip" \
    -p "$probes_sets_path$probes_filepath" \
    -c "$campaign_selected"
  done
}

for target in "${target_direction_list[@]}"; do
  do_measurement_campaign_to_target "$target" "$campaign_name"
done


