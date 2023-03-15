#!/bin/bash

num_probes_array=(100 300 500 1000)
alpha_array=(0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1)
#areas_array=("North-Central" "North-East" "South-Central" "South-East" "West" "WW")
areas_array=("North-Central" "WW")
root_servers_ip_diretions=("198.41.0.4" "199.9.14.201" "192.33.4.12" "199.7.91.13" 
    "192.203.230.10" "192.5.5.241" "192.112.36.4" "198.97.190.53" 
    "192.36.148.17" "192.58.128.30" "193.0.14.129" "199.7.83.42" "202.12.27.33")
root_server_ip_direcction_selected="192.5.5.241"
campaign_log_file="Campaign_"$root_server_ip_direcction_selected"_$(date +%F_%T).txt"
alpha_tunning_log_file="Alpha_tunning_"$root_server_ip_direcction_selected"_$(date +%F_%T).txt"
measurement_filename_array=(
  "North-Central_100_192.5.5.241"
  "North-Central_300_192.5.5.241" 
  "North-Central_500_192.5.5.241" 
  "North-Central_1000_192.5.5.241" 
  "WW_100_192.5.5.241" 
  "WW_300_192.5.5.241"
  "WW_500_192.5.5.241" 
  "WW_1000_192.5.5.241")
results_filenames_array=()
probes_filenames_array=()

fill_results_filenames_array()
{
  for area in "${areas_array[@]}"; do
    for num_probes in "${num_probes_array[@]}"; do
      for alpha in "${alpha_array[@]}"; do
        results_filenames_array+=($area"_"$num_probes"_"$alpha"_"$root_server_ip_direcction_selected)
      done
    done
  done
}

fill_probes_filenames_array()
{
  for area in "${areas_array[@]}"; do
    for num_probes in "${num_probes_array[@]}"; do
      probes_filenames_array+=("probes_sets/"$area"_"$num_probes.json)
    done
  done
}


measurement_big()
{
  for area in "${areas_array[@]}"; do
    for num_probes in "${num_probes_array[@]}"; do
      probes_file_name="probes_sets/"$area"_"$num_probes.json
      output_name_file=$area"_"$num_probes"_1_"$root_server_ip_direcction_selected

      echo """

      Measurement to $root_server_ip_direcction_selected using $probes_file_name 
      started.

      """

      #Start the measurements and save the results in a txt file
      ./igreedy.sh -m $root_server_ip_direcction_selected \
      -p "$probes_file_name" \
      -o "$output_name_file" \
      -a 1 \
      | tee -a "$campaign_log_file"

      echo "########################################" >> "$campaign_log_file"

      echo """

      Measurement to $root_server_ip_direcction_selected using $probes_file_name 
      finished.

      """
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

analyze_alpha()
{
  for measurement_filename in "${measurement_filename_array[@]}"; do
    for alpha in "${alpha_array[@]}"; do
      output_filename=$measurement_filename"_$alpha"
      ./igreedy.sh -i "datasets/measurement/$measurement_filename" \
      -o "$output_filename" \
      -a "$alpha" \
      | tee -a "$alpha_tunning_log_file"
    done 
    echo "########################################" >> "$alpha_tunning_log_file"
  done
}

analyze_alpha