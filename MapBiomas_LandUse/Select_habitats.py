# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 10:17:39 2023

@author: pablo
"""

!pip install rasterio numpy

import rasterio
import numpy as np

def load_raster(file_path):
    with rasterio.open(file_path) as dataset:
        data = dataset.read(1)
        return data

def select_values(data, values_to_keep, nodata_value):
    selected_data = np.where(np.isin(data, values_to_keep), data, nodata_value)
    return selected_data

def save_to_raster(output_file, data, source_dataset, nodata_value):
    with rasterio.open(
        output_file,
        'w',
        driver='GTiff',
        height=data.shape[0],
        width=data.shape[1],
        count=1,
        dtype=data.dtype,
        crs=source_dataset.crs,
        transform=source_dataset.transform,
        nodata=nodata_value,
    ) as dest:
        dest.write(data, 1)

def main(input_raster, output_raster, values_to_keep):
    data = load_raster(input_raster)
    nodata_value = -9999  # Custom NoData value

    selected_data = select_values(data, values_to_keep, nodata_value)

    with rasterio.open(input_raster) as src_dataset:
        save_to_raster(output_raster, selected_data, src_dataset, nodata_value)

if __name__ == "__main__":
    input_raster_file = "C:/Users/pablo/Documents/IRD/data/Mapbiomas/mapbiomas-brazil-collection-70-paraiba-2021.tif"
    output_raster_file = "C:/Users/pablo/Documents/IRD/data/Mapbiomas/2021_habitats_clean.tif"

    # Define the specific raster values you want to keep in the new raster
    values_to_keep = [1, 2, 3, 5]  # Replace [1, 2, 3] with your desired values

    main(input_raster_file, output_raster_file, values_to_keep)
