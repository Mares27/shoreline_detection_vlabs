import os
import json
from shoreline_detection import shoreline_detection
import shutil




def load_config(path_to_config_file):
    '''load the configuration file'''
    with open(path_to_config_file) as f:
        config = json.load(f)
    return config


def init_dir(output_dir): 
    '''create directories to store output'''
    
    if(output_dir[-1] != "/"):
        output_dir += "/"

    if(os.path.exists(output_dir)):
        shutil.rmtree(output_dir)
	
    os.mkdir(output_dir)
    
    edges_results_dir = output_dir + "/" + "image/"
    image_geolocalized = output_dir + "/" + "image_geolocalized/"
    
    os.mkdir(edges_results_dir)
    os.mkdir(image_geolocalized)

    return  edges_results_dir, image_geolocalized
    

if __name__ == "__main__":
    
    print("Please enter the configuration json INPUT file name:")
    file_name = input()

    ##load configuration file
    config = load_config(file_name)
    
    ##initialize the output directory to save results
    edges_results_dir, image_geolocalized_dir  = init_dir(config["output_directory"])
    
    ##load the path to the directory of the input data
    path_to_data = config["path_to_data"]
    
    ##number of the neighborhors defining the size of the kernel implemented to reduce the speckling effect
    k = config["k"]
    
    ##load output file name    
    name = config["output_name_tif"]
    
    ##return an image
    obj = shoreline_detection.shoreline(path_to_data, k, edges_results_dir, image_geolocalized_dir, name)
    