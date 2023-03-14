#!/bin/bash

num_probes_array=(100 300 500 1000 2000)
#areas_array=("North-Central" "North-East" "South-Central" "South-East" "West" "WW")
areas_array=("North-Central" "WW")
root_servers_ip_diretions=("198.41.0.4" "199.9.14.201" "192.33.4.12" "199.7.91.13" 
    "192.203.230.10" "192.5.5.241" "192.112.36.4" "198.97.190.53" 
    "192.36.148.17" "192.58.128.30" "193.0.14.129" "199.7.83.42" "202.12.27.33")
root_server_ip_direcction_selected="192.5.5.241"
log_file_name="Campaign_"$root_server_ip_direcction_selected"_$(date +%F_%T).txt"

measurement_big()
{
  for area in "${areas_array[@]}"; do
    for num_probes in "${num_probes_array[@]}"; do
      probes_file_name="probes_sets/"$area"_"$num_probes.json
      output_name_file=$area"_"$num_probes"_"$root_server_ip_direcction_selected

      echo """

      Measurement to $root_server_ip_direcction_selected using $probes_file_name 
      started.

      """

      #Start the measurements and save the results in a txt file
      ./igreedy.sh -m $root_server_ip_direcction_selected \
      -p "$probes_file_name" \
      -o "$output_name_file" \
      | tee -a "$log_file_name"

      echo "########################################" >> "$log_file_name"

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
}


measurement_big