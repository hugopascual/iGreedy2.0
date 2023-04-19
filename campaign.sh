#!/bin/bash

#areas_array=("WW")
areas_array=("North-Central")
#areas_array=("North-Central" "WW")
#areas_array=("North-Central" "North-East" "South-Central" "South-East" "West" "WW")
num_probes_array=(100 300 500 1000)

#areas_array=("Europe_countries")
#num_probes_array=(5 10 15)

root_servers_ip_directions=(
"198.41.0.4" "199.9.14.201" "192.33.4.12" "199.7.91.13" "192.203.230.10"
"192.5.5.241" "192.112.36.4" "198.97.190.53" "192.36.148.17" "192.58.128.30"
"193.0.14.129" "199.7.83.42" "202.12.27.33")
root_servers_names=(
"root_servers_A.json" "root_servers_B.json" "root_servers_C.json"
"root_servers_D.json" "root_servers_E.json" "root_servers_F.json"
"root_servers_G.json" "root_servers_H.json" "root_servers_I.json"
"root_servers_J.json" "root_servers_K.json" "root_servers_L.json"
"root_servers_M.json"
)
root_servers_directory_name="datasets/ground-truth/root_servers/"

cloudfare_servers_ip_directions=(
"104.16.123.96"
)
cloudfare_servers_names=(
"cloudfare_servers_europe.json"
)
cloudfare_servers_directory_name="datasets/ground-truth/cloudfare/"

servers_ip_directions=(
"104.16.123.96"
)
servers_names=(
"cloudfare_servers_europe.json"
)
servers_directory_name="datasets/ground-truth/cloudfare/"

alpha_array=(0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1)
threshold_array=(-1 0.5 1 5 10 20 30)

probes_filenames_array=()
probes_filepaths_array=()

campaign_name="North-Central_20230418"
#campaign_name="Europe_countries_20230413"
campaign_directories_names_array=()

fill_probes_arrays()
{
  for area in "${areas_array[@]}"; do
    for num_probes in "${num_probes_array[@]}"; do
      probes_filenames_array+=($area"_"$num_probes)
      probes_filepaths_array+=("datasets/probes_sets/"$area"_"$num_probes.json)
    done
  done
}

fill_campaign_directories_names_array()
{
  for ip in "${servers_ip_directions[@]}"; do
    campaign_directories_names_array+=("$ip"_"$campaign_name")
  done
}

measurement_campaign_to_ip()
{
  ip=$1
  campaign_selected=$2
  for probes_filepath in "${probes_filepaths_array[@]}"; do
    # echo the command used
    echo ./igreedy.sh -m "$1" \
    -p "$probes_filepath" \
    -c "$campaign_selected"
    echo ""
    # Start the measurement
    ./igreedy.sh -m "$1" \
    -p "$probes_filepath" \
    -c "$campaign_selected"
  done
}

alpha_iterations_results()
{
  groundtruth_comparison_file=$1
  campaign_selected=$2
  campaign_measurements_directory="datasets/measurements/campaigns/$2"

  for measurement in "$campaign_measurements_directory"/*; do
    for alpha in "${alpha_array[@]}"; do
      ./igreedy.sh -i "$measurement" \
      -a "$alpha" \
      -g "$groundtruth_comparison_file" \
      -c "$campaign_selected""_alpha"
    done
  done
}

threshold_iteration_results()
{
  groundtruth_comparison_file=$1
  campaign_selected=$2
  campaign_measurements_directory="datasets/measurements/campaigns/$2"

  for measurement in "$campaign_measurements_directory"/*; do
    for threshold in "${threshold_array[@]}"; do
      ./igreedy.sh -i "$measurement" \
      -t "$threshold" \
      -g "$groundtruth_comparison_file" \
      -c "$campaign_selected""_threshold"
    done
  done
}

fill_probes_arrays
fill_campaign_directories_names_array
for index in "${!campaign_directories_names_array[@]}"; do

  ip_selected="${servers_ip_directions[$index]}"
  campaign_selected="${campaign_directories_names_array[$index]}"
  gt_server_filename="${servers_names[$index]}"

  # Make measurements with all probes files to an ip
  measurement_campaign_to_ip "$ip_selected" "$campaign_selected"

  # Generate results with alpha iterations
  alpha_iterations_results \
  "datasets/ground-truth/cloudfare/$gt_server_filename" \
  "$campaign_selected"

  # Generate results with threshold iterations
  threshold_iteration_results \
  "datasets/ground-truth/cloudfare/$gt_server_filename" \
  "$campaign_selected"
done
