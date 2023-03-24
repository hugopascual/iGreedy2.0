#!/bin/bash

num_probes_array=(100 300 500 1000)
alpha_array=(0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1)
#areas_array=("North-Central" "North-East" "South-Central" "South-East" "West" "WW")
#areas_array=("North-Central" "WW")
areas_array=("North-Central")
root_server_ip_direcction_selected="192.5.5.241"
campaign_log_file="Campaign_"$root_server_ip_direcction_selected"_$(date +%F_%T).txt"
alpha_tunning_log_file="Alpha_tunning_"$root_server_ip_direcction_selected"_$(date +%F_%T).txt"
measurements_filenames_array=()
probes_filenames_array=()
probes_filepaths_array=()

fill_measurements_filenames_filenames_array()
{
  for probes_filename in "${probes_filenames_array[@]}"; do
    measurements_filenames_array+=($probes_filename"_"$root_server_ip_direcction_selected.json)
  done
}

fill_probes_filenames_array()
{
  for area in "${areas_array[@]}"; do
    for num_probes in "${num_probes_array[@]}"; do
      probes_filenames_array+=($area"_"$num_probes)
      probes_filepaths_array+=("probes_sets/"$area"_"$num_probes.json)
    done
  done
}

measurement_manual()
{
  ./igreedy.sh -m "192.203.230.10" \
  -p "probes_sets/North-Central_1000.json" \
  -o "North-Central_1000_192.203.230.10" \
  | tee -a "Single_North-Central_1000_$(date +%F_%T).txt"

  ./igreedy.sh -i "datasets/measurement/192.5.5.241-50948678-1678879591" \
  -o "North-Central_100_1_192.5.5.241" \
  -a "2"
}

measurement_big()
{
  for probes_filepath in "${probes_filepaths_array[@]}"; do
      echo """
Measurement to $root_server_ip_direcction_selected using $probes_filepath 
started."""

      echo ./igreedy.sh -m $root_server_ip_direcction_selected \
      -p "$probes_filepath" \
      | tee -a "$campaign_log_file"

      #Start the measurements and save the results in a txt file
      ./igreedy.sh -m $root_server_ip_direcction_selected \
      -p "$probes_filepath" \
      | tee -a "$campaign_log_file"

      echo "########################################" >> "$campaign_log_file"

      echo """
Measurement to $root_server_ip_direcction_selected using $probes_filepath 
finished."""
  done
}

analyze_alpha()
{
  for measurement_filename in "${measurements_filenames_array[@]}"; do
    for alpha in "${alpha_array[@]}"; do
      echo ./igreedy.sh -i "datasets/measurement/$measurement_filename" \
      -a "$alpha" \
      | tee -a "$alpha_tunning_log_file"

      ./igreedy.sh -i "datasets/measurement/$measurement_filename" \
      -a "$alpha" \
      | tee -a "$alpha_tunning_log_file"
    done 
    echo "########################################" >> "$alpha_tunning_log_file"
  done
}

fill_probes_filenames_array
fill_measurements_filenames_filenames_array

measurement_big
analyze_alpha
