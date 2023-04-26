#!/bin/bash

###############################################################################
# Constants
probes_sets_path="datasets/probes_sets/"
probes_section_path="datasets/probes_section/"
measurements_campaigns_path="datasets/measurements/campaigns/"
light_factor="light-factor_0.18"

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
###############################################################################
alpha_array=(0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1)
threshold_array=(-1 0.5 1 5 10 20 30)
###############################################################################
fill_probes_arrays()
{
  for area in "${areas_array[@]}"; do
    for num_probes in "${num_probes_array[@]}"; do
      probe_file_name="$area"_"$num_probes"
      probes_filepaths_array+=("$probes_path$probe_file_name.json")
    done
  done
}

do_measurement_campaign_to_target()
{
  ip=$1
  campaign_selected=$2
  probes_filepaths_array=()
  fill_probes_arrays
  for probes_filepath in "${probes_filepaths_array[@]}"; do
    # echo the command used
    echo ./igreedy.sh -m "$ip" \
    -p "$probes_filepath" \
    -c "$campaign_selected"
    echo ""
    # Start the measurement
    ./igreedy.sh -m "$ip" \
    -p "$probes_filepath" \
    -c "$campaign_selected"
  done
}

fill_campaign_directories_names_array()
{
  campaign_name=$1
  for target in "${target_directions[@]}"; do
    campaign_names_array+=("$target"_"$campaign_name")
  done
}

alpha_iterations_results()
{
  groundtruth_comparison_file=$1
  campaign_selected=$2
  measurements_campaign_directory="$measurements_campaigns_path$campaign_selected"

  for measurement in "$measurements_campaign_directory"/*; do
    for alpha in "${alpha_array[@]}"; do
      echo ./igreedy.sh -i "$measurement" \
      -a "$alpha" \
      -g "$groundtruth_comparison_file" \
      -c "$campaign_selected""_alpha_$light_factor"

      ./igreedy.sh -i "$measurement" \
      -a "$alpha" \
      -g "$groundtruth_comparison_file" \
      -c "$campaign_selected""_alpha_$light_factor"
    done
  done
}

threshold_iteration_results()
{
  groundtruth_comparison_file=$1
  campaign_selected=$2
  measurements_campaign_directory="$measurements_campaigns_path$campaign_selected"

  for measurement in "$measurements_campaign_directory"/*; do
    for threshold in "${threshold_array[@]}"; do
      echo ./igreedy.sh -i "$measurement" \
      -t "$threshold" \
      -g "$groundtruth_comparison_file" \
      -c "$campaign_selected""_threshold_$light_factor"

      ./igreedy.sh -i "$measurement" \
      -t "$threshold" \
      -g "$groundtruth_comparison_file" \
      -c "$campaign_selected""_threshold_$light_factor"
    done
  done
}

get_results_and_validations()
{
  campaign_names_array=()
  fill_campaign_directories_names_array "$campaign_name"

  for index in "${!campaign_names_array[@]}"; do
    target_selected="${target_directions[$index]}"
    campaign_selected="${campaign_names_array[$index]}"
    gt_server_filename="${servers_names[$index]}"

    # Make measurements with all probes files to target
    #do_measurement_campaign_to_target \
    #"$target_selected" \
    #"$campaign_selected"

    # Generate results with alpha iterations
    alpha_iterations_results \
    "$servers_directory_name$gt_server_filename" \
    "$campaign_selected"

    # Generate results with threshold iterations
    threshold_iteration_results \
    "$servers_directory_name$gt_server_filename" \
    "$campaign_selected"

  done
}

## Campaign to cloudfare servers using North-Central probes_sets
#campaign_name="North-Central_20230418"
## Target to measure
#target_directions=()
#target_directions+=("${cloudfare_servers_ip_directions[@]}")
## Probes used in measurement
#probes_path=$probes_sets_path
#areas_array=("North-Central")
#num_probes_array=(100 300 500 1000)
## GT Comparison
#servers_directory_name=$cloudfare_servers_directory_name
#servers_names=()
#servers_names+=("${cloudfare_servers_names[@]}")
#get_results_and_validations

## Campaign to cloudfare servers using Europe-countries probes_sets
#campaign_name="Europe-countries_20230413"
## Target to measure
#target_directions=()
#target_directions+=("${cloudfare_servers_ip_directions[@]}")
## Probes used in measurement
#probes_path=$probes_sets_path
#areas_array=("Europe-countries")
#num_probes_array=(5 10 15)
## GT Comparison
#servers_directory_name=$cloudfare_servers_directory_name
#servers_names=()
#servers_names+=("${cloudfare_servers_names[@]}")
#get_results_and_validations

## Campaign to cloudfare servers using North-Central probes_sets
#campaign_name="North-Central_20230410"
## Target to measure
#target_directions=()
#target_directions+=("${root_servers_ip_directions[@]}")
## Probes used in measurement
#probes_path=$probes_sets_path
#areas_array=("North-Central")
#num_probes_array=(100 300 500 1000)
## GT Comparison
#servers_directory_name=$root_servers_directory_name
#servers_names=()
#servers_names+=("${root_servers_names[@]}")
#get_results_and_validations

## Campaign to cloudfare servers using North-Central probes_sets
#campaign_name="North-Central-section_20230425"
## Target to measure
#target_directions=()
#target_directions+=("${root_servers_ip_directions[@]}")
## Probes used in measurement
#probes_path=$probes_section_path
#areas_array=("North-Central-section")
#num_probes_array=(1 1.5 2)
## GT Comparison
#servers_directory_name=$root_servers_directory_name
#servers_names=()
#servers_names+=("${root_servers_names[@]}")
#get_results_and_validations

# Campaign to cloudfare servers using North-Central probes_sets
campaign_name="North-Central-section_20230426"
# Target to measure
target_directions=()
target_directions+=("${cloudfare_servers_ip_directions[@]}")
# Probes used in measurement
probes_path=$probes_section_path
areas_array=("North-Central-section")
num_probes_array=(1 1.5 2)
# GT Comparison
servers_directory_name=$cloudfare_servers_directory_name
servers_names=()
servers_names+=("${cloudfare_servers_names[@]}")
get_results_and_validations


