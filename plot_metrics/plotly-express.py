import plotly.express as px
import pandas as pd
import geopandas as gpd
import json

def json_file_to_dict(file_path: str) -> dict:
    with open(file_path) as file:
        raw_json = file.read()
    
    return json.loads(raw_json)

def plot_metrics():
    filepath = "ground_truth_tests/ground_truth_metrics/North-Central_campaign_20230324.csv"
    df = pd.read_csv(filepath)
    metric = "recall"
    fig = px.line(df, x="alpha", y=metric, color='num_probes')
    fig.update_layout(title = "Metrics of {} in relation to alpha and number \
                      of probes".format(metric))
    fig.show()

def plot_geo_example():
    df = px.data.gapminder().query("year == 2007")

    plot = px.scatter_geo(df, locations="iso_alpha")
    plot.show()

def alpha2_code_to_alpha3(alpha2: str):
    all_countries_path = "datasets/countries_lists/all_countries.json"
    all_countries_list = json_file_to_dict(all_countries_path)
    for country in all_countries_list:
        if alpha2 == country["alpha-2"]:
            return country["alpha-3"]

def plot_geo():
    filepath = "ground_truth_tests/ground_truth_metrics/North-Central_campaign_20230324.json"
    metrics_sets_dict = json_file_to_dict(filepath)[-1]["sets"]
    geo_dict =  {
        "alpha2": [],
        "type": []
    }
    metrics_sets_names = [
        "true_positive_countries", 
        "false_positive_countries",
        "true_negative_countries",
        "false_negative_countries",
        "instances_outside_true_detected",
        "instances_outside_false_detected"]

    for set_name in metrics_sets_names:
        for country_code in metrics_sets_dict[set_name]:
            geo_dict["alpha2"].append(alpha2_code_to_alpha3(country_code)) 
            geo_dict["type"].append(set_name)

    df = pd.DataFrame(geo_dict)

    plot = px.scatter_geo(df, locations="alpha2", color="type")
    plot.show()

def get_measurement_probes_location(measurement_path: str):
    measurement_path = "../datasets/measurement/campaigns/20230324/North-Central_1000_192.5.5.241.json"
    #measurement_path = "../datasets/measurement/campaigns/20230324/North-Central_1000_192.5.5.241.json"
    measurement_dict = json_file_to_dict(measurement_path)

results_analisis_markers_locations = {
    "type": [],
    "latitude": [],
    "longitude": []
}

results_analisis_probes_locations = {
    "type": [],
    "latitude": [],
    "longitude": []
}

def get_gt_intances_locations():
    filepath = "datasets/ground-truth/root_servers/root_servers_A.json" 
    
    df = pd.DataFrame(json_file_to_dict(filepath)["Sites"])
    df = df[["Country", "Town", "Latitude", "Longitude" ]]
    df.drop_duplicates(subset=['Town'], inplace=True)

    return df

def get_results_intances_locations():
    filepath = "results/campaings/20230324/North-Central_1000_192.5.5.241_1.0.json" 
    
    df = pd.DataFrame(json_file_to_dict(filepath)["anycast_intances"])

    print(df)
    return df

get_results_intances_locations()
