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

def get_gt_intances_locations():
    filepath = "datasets/ground-truth/root_servers/root_servers_F.json" 
    
    df = pd.DataFrame(json_file_to_dict(filepath)["Sites"])
    df = df[["Country", "Town", "Latitude", "Longitude" ]]
    df.rename(
        columns={
        "Country": "country_code", 
        "Town": "city", 
        "Latitude": "latitude", 
        "Longitude": "longitude"},
        inplace=True)
    df.drop_duplicates(subset=['city'], inplace=True)
    df["type"] = "gt_instance"

    return df

def get_results_intances_locations():
    filepath = "results/campaigns/20230324/North-Central_1000_192.5.5.241_1.0.json" 
    anycast_instances = json_file_to_dict(filepath)["anycast_intances"]
    markers = []
    for instance in anycast_instances:
        markers.append(instance["marker"])
    
    df = pd.DataFrame(markers)
    df = df[["code_country", "city", "latitude", "longitude"]]
    df.rename(
        columns={
        "code_country": "country_code"},
        inplace=True)
    df["type"] = "result_instance"

    return df

def get_results_probes_locations():
    filepath = "results/campaigns/20230324/North-Central_1000_192.5.5.241_1.0.json" 
    anycast_instances = json_file_to_dict(filepath)["anycast_intances"]
    circles = []
    for instance in anycast_instances:
        circles.append(instance["circle"])
    
    df = pd.DataFrame(circles)
    df = df[["id", "latitude", "longitude"]]
    df.rename(
        columns={
        "id": "hostname"},
        inplace=True)
    df['city'] = df.loc[:, 'hostname']
    df["type"] = "result_probe"

    return df

def get_measurement_probes_locations():
    filepath = "datasets/measurement/campaigns/20230324/North-Central_1000_192.5.5.241.json" 
    measurement_probes = json_file_to_dict(filepath)["measurement_results"]
    
    df = pd.DataFrame(measurement_probes)
    df = df[["hostname", "latitude", "longitude"]]
    df['city'] = df.loc[:, 'hostname']
    df["type"] = "probe"

    return df

def plot_gt_and_results():
    df = pd.concat([get_gt_intances_locations(), 
                    get_results_intances_locations(),
                    get_results_probes_locations(),
                    #get_measurement_probes_locations()
                    ])

    plot = px.scatter_geo(df, 
                        lat="latitude", 
                        lon="longitude", 
                        hover_name="city",
                        color="type")
    plot.show()

    df.sort_values("country_code", inplace=True)
    df.to_csv("plot_metrics/test.csv")
    return df

plot_gt_and_results()
