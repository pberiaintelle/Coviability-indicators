install.packages("sf")
install.packages("dplyr")
install.packages("ggplot2")
install.packages("scico")
install.packages("rnaturalearth")
install.packages("rnaturalearthdata")
install.packages("purrr")
install.packages("smoothr")
install.packages("raster")
install.packages("stars")
# load packages
library(sf)
library(dplyr)
library(ggplot2)
library(scico)
library(rnaturalearth)
library(purrr)
library(smoothr)
library(rgbif)
library(raster)
library(stars)
# Load geojson
geojson_file <- "C:/Users/pablo/Documents/IRD/data/bbox/bboxParaiba.geojson"
bbox_sf <- st_read(geojson_file)
# world map
worldMap <- ne_countries(scale = "medium", type = "countries", returnclass = "sf")

# country subset
CRpoly <- worldMap %>% filter(sovereignt == "Brazil")
#Plot
ggplot() +
  geom_sf(data = bbox_sf) +
  coord_sf()
# Load geojson MUNICIPALITIES
municipalities <- "C:/Users/pablo/Documents/IRD/data/bbox/bboxParaiba.geojson"

# Clip Brazil polygon to the bounding box
# Show the CRS of bbox_sf
crs_bbox <- st_crs(bbox_sf)
print(crs_bbox)
CRpoly <- st_set_crs(CRpoly, st_crs(bbox_sf))
print(st_crs(CRpoly))
# Clip Brazil polygon to the bounding box
clipped_CRpoly <- st_intersection(CRpoly, bbox_sf)
# Load geojson MUNICIPALITIES
municipalities <- "C:/Users/pablo/Documents/IRD/SRC/bboxMunicipalities.geojson"
mun <- st_read(municipalities)
mun <- st_set_crs(mun, st_crs(bbox_sf))
clipped_mun <- st_intersection(mun, bbox_sf)
#Load points
csv_file <- "C:/Users/pablo/Documents/IRD/data/iNaturalist/iNaturalistGbifIUCNmerged.csv"
data <- read.csv(csv_file)
summary(data)
# species and lat long data
PXY <- data %>%
  select(scientific_name, longitude, latitude) %>%
  na.omit()
# to sf object, specifying variables with coordinates and projection
PXYsf <- st_as_sf(PXY, coords = c("longitude", "latitude"), crs = 4674) %>%
  group_by(scientific_name) %>%
  summarize()
#Plot points
ggplot() +
  geom_sf(data = clipped_CRpoly, fill = "lightblue", color = "black", alpha = 0.5) +
  geom_sf(data = PXYsf, aes(color = scientific_name), size = 2) +
  scale_color_discrete(guide = FALSE) +
  coord_sf(crs = st_crs(4674)) +
  theme_minimal()
# Plot points, polygons, and grid
ggplot() +
  geom_sf(data = clipped_CRpoly, fill = "lightblue", color = "black", alpha = 0.5) +
  geom_sf(data = PXYsf, aes(color = scientific_name), size = 2) +
  geom_sf(data = PGrid, fill = NA, color = "red", alpha = 0.5) +  # Add this line for the grid
  scale_color_discrete(guide = FALSE) +
  coord_sf(crs = st_crs(4674)) +
  theme_minimal()
# grid
PGrid <- bbox_sf %>%
  st_make_grid(cellsize = 0.01) %>%
  #st_intersection(clipped_CRpoly) %>%
  st_cast("MULTIPOLYGON") %>%
  st_sf(crs=4674) %>%
  mutate(cellid = row_number())

pgrid <- bbox_sf %>%
  st_make_grid(cellsize = c(100, 100)) %>%
  st_cast("MULTIPOLYGON") %>%
  st_intersection(bbox_sf)%>%
  st_sf(crs = st_crs(bbox_sf)) %>%
  mutate(cellid = row_number())

tifpath=system.file("C:/Users/pablo/Documents/IRD/data/Landsat/ndvi_image.tif", package = "stars")
tif=read_stars(tifpath)
sf=st_as_sf(tif)
# Replace with the correct absolute file path
tifpath <- "C:/Users/pablo/Documents/IRD/data/2010popbbox.tif"

# Read the GeoTIFF file as a raster object
raster_obj <- raster(tifpath)

# Convert raster to polygons
polygons <- rasterToPolygons(raster_obj, dissolve = TRUE)  # You might need to adjust parameters

# Convert polygons to sf object
polygons_sf <- st_as_sf(polygons)

# Print the sf object summary
print(polygons_sf)
# empty grid
ggplot() +
  geom_sf(data = clipped_CRpoly, fill = "lightblue", color = "black", alpha = 0.5) +
  geom_sf(data = PXYsf, aes(color = scientific_name), size = 2) +
  geom_sf(data = PGrid, fill = NA, color = "red", alpha = 0.5) +  # Add this line for the grid
  scale_color_discrete(guide = FALSE) +
  coord_sf(crs = st_crs(4674)) +
  theme_minimal()

#Load grid made from a raster
gridpath <- "C:/Users/pablo/Documents/IRD/data/GBIF/grid_pixel.geojson"
rgrid <- st_read(gridpath)
rgrid <- st_set_crs(rgrid, st_crs(bbox_sf))

# cell richness per municipality
richness_grid_mun <- clipped_mun %>%
  st_join(PXYsf) %>%
  mutate(overlap = ifelse(!is.na(scientific_name), 1, 0)) %>%
  group_by(CD_MUN) %>%
  summarize(num_species = sum(overlap))

# cell richness per grid cell
richness_grid <- PGrid %>%
  st_join(PXYsf) %>%
  mutate(overlap = ifelse(!is.na(scientific_name), 1, 0)) %>%
  group_by(cellid) %>%
  summarize(num_species = sum(overlap))%>%
  st_intersection(clipped_mun)
# plot
richness <-
  ggplot(richness_grid) +
 # geom_sf(data = neighbours, color = "white") +
  #geom_sf(data = clipped_CRpoly, fill = "grey", size = 0.1) +
  geom_sf(aes(fill = num_species), color = NA) +
  scale_fill_scico(
    palette = "davos",
    direction = -1,
    end = 0.9,
    name = "species richness",
    limits = c(0, 10)  # Set the color scale limits
  )+
  theme(
    plot.background = element_rect(fill = "#f1f2f3"),
    panel.background = element_rect(fill = "#2F4051"),
    panel.grid = element_blank(),
    legend.position = "bottom",
    line = element_blank(),
    rect = element_blank()
  ) + labs(fill = "richness")
richness

# Specify the path for the output GeoJSON file
output_geojson <- "C:/Users/pablo/Documents/IRD/data/GBIF/richness_municipality.geojson"
output_geojson2 <- "C:/Users/pablo/Documents/IRD/data/GBIF/richness_grid.geojson"
# Write the sf object to a GeoJSON file
st_write(richness_grid_mun, output_geojson,geometry_column = "geometry", driver = "GeoJSON")
st_write(richness_grid, output_geojson2,geometry_column = "geometry", driver = "GeoJSON")
