## Fishing Pressure COG's

### Tasks and Progress

1. Downloaded Fishing Pressure Shapefile from Google Drive
2. Rasterized after reconverting Pressure SHP to new EPSG:3857
3. FP_Total and FP_NC were resulting layers, 1 km squares as 10km and 100km caused errors
4. Used TIF-to-COG Python script to create COG's
5. Edited Darren's STAC template to fit fishing pressure
6. Uploaded STAC.json and COG's for both files to AWS Fishing Pressure Folder

### Potential Errors and Next Steps

1. COG's are based off of 1km squares instead of 10km squares, attempts to display the pixels and have them line up with the shapefile had the pixels off by varying degrees. 
  Could be fixed through further experimentation with Raster tool and reconverting the TIFs prior to making them COGs.

2. Need to check and ensure that the COG's are viewable online. They are verified within the server, but would be nice to know that they actually work. 
