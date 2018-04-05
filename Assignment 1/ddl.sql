CREATE TABLE graffiti_fs(
  creation_date DATE,
  status TEXT,
  completion_date DATE,
  service_request_number TEXT,
  type_of_service_request TEXT,
  surface_type TEXT,
  graffiti_location TEXT,
  street_address TEXT,
  zip_code INT,
  x_coordinate FLOAT,
  y_coordinate FLOAT,
  ward INT,
  police_district INT,
  community_area INT,
  ssa INT,
  latitude FLOAT,
  longitude FLOAT,
  location TEXT
);

CREATE TABLE vacant_fs(
  service_request_type TEXT,
  service_request_number TEXT,
  date_service_request_received DATE,
  location_of_building_on_lot TEXT,
  is_bldg_dangerous_hazardous TEXT,
  bldg_boarded TEXT,
  is_bldg_open TEXT,
  vacant_or_occupied TEXT,
  vacant_due_to_fire BOOLEAN,
  people_on_property BOOLEAN,
  address_street_number INT,
  address_street_direction TEXT,
  address_street_name TEXT,
  address_street_suffix TEXT,
  zip_code INT,
  x_coordinate FLOAT,
  y_coordinate FLOAT,
  ward INT,
  police_district INT,
  community_area INT,
  latitude FLOAT,
  longitude FLOAT,
  location TEXT
);


CREATE TABLE alley_fs(
  creation_date DATE,
  status TEXT,
  completion_date DATE,
  service_request_number TEXT,
  type_of_service_request TEXT,
  street_address TEXT,
  zip_code INT,
  x_coordinate FLOAT,
  y_coordinate FLOAT,
  ward INT,
  police_district INT,
  community_area INT,
  latitude FLOAT,
  longitude FLOAT,
  location TEXT
);

CREATE TABLE alley(
  creation_date DATE,
  status TEXT,
  completion_date DATE,
  service_request_number TEXT,
  type_of_service_request TEXT,
  street_address TEXT,
  zip_code INT,
  x_coordinate FLOAT,
  y_coordinate FLOAT,
  ward INT,
  police_district INT,
  community_area INT,
  latitude FLOAT,
  longitude FLOAT,
  location TEXT,
  fips INT
);

CREATE TABLE graffiti(
  creation_date DATE,
  status TEXT,
  completion_date DATE,
  service_request_number TEXT,
  type_of_service_request TEXT,
  surface_type TEXT,
  graffiti_location TEXT,
  street_address TEXT,
  zip_code INT,
  x_coordinate FLOAT,
  y_coordinate FLOAT,
  ward INT,
  police_district INT,
  community_area INT,
  ssa INT,
  latitude FLOAT,
  longitude FLOAT,
  location TEXT,
  fips TEXT
);

CREATE TABLE vacant(
  service_request_type TEXT,
  service_request_number TEXT,
  date_service_request_received DATE,
  location_of_building_on_lot TEXT,
  is_bldg_dangerous_hazardous TEXT,
  bldg_boarded TEXT,
  is_bldg_open TEXT,
  vacant_or_occupied TEXT,
  vacant_due_to_fire BOOLEAN,
  people_on_property BOOLEAN,
  address_street_number INT,
  address_street_direction TEXT,
  address_street_name TEXT,
  address_street_suffix TEXT,
  zip_code INT,
  x_coordinate FLOAT,
  y_coordinate FLOAT,
  ward INT,
  police_district INT,
  community_area INT,
  latitude FLOAT,
  longitude FLOAT,
  location TEXT,
  street_address TEXT,
  fips INT
);

CREATE TABLE combined_data(
  type_of_service_request TEXT,
  service_request_number TEXT,
  creation_date DATE,
  completion_date DATE,
  days_to_complete INT,
  street_address TEXT,
  zip_code INT,
  x_coordinate FLOAT,
  y_coordinate FLOAT,
  latitude FLOAT,
  longitude FLOAT,
  ward INT,
  police_district INT,
  community_area INT,
  fips TEXT,
  block_group INT
);

CREATE TABLE census_block (
total_population int,
white int,
black int,
asian int,
hispanic int,
poverty int,
median_income int,
per_capita_income int,
total_employed int,
unemployed int,
median_home_value int,
block_group INT, 
county TEXT, 
state INT, 
tract TEXT
);

CREATE TABLE census_tract (
total_population INT,
white INT,
black INT,
asian INT,
hispanic INT,
poverty INT,
median_income INT,
per_capita_income INT,
total_employed INT,
unemployed INT,
median_home_value INT,
county TEXT,
state INT,
tract TEXT
);

metadata = {'B02001_002E' : {'name': "white",'dtype' : 'int'},
                      'B02001_003E' : {'name': "black", 'dtype' : 'int'},
                      'B02001_005E' : {'name': "asian", 'dtype' : 'int'},
                      'B03001_003E' : {'name': "hispanic", 'dtype' : 'int'},
                      'B19013_001E' : {'name': "median_income", 'dtype' : 'int'},
                      'B19301_001E' : {'name': "per_capita_income", 'dtype' : 'int'},
                      'B23025_001E' : {'name': "total_employed", 'dtype' : 'int'},
                      'B23025_005E' : {'name': "unemployed", 'dtype' : 'int'},
                      'B17001_002E' : {'name': "poverty", 'dtype' : 'int'},
                      'B01003_001E' : {'name': "total_population", 'dtype' : 'int'},
                      'B25077_001E' : {'name': "median_home_value", 'dtype' : 'int'}}


'''
INSERT INTO combined_data
SELECT
service_request_type,
service_request_number,
date_service_request_received as creation_date,
'' as completion_date,
'' as days_to_complete,
street_address,
zip_code,
x_coordinate,
y_coordinate,
latitude,
longitude,
ward,
police_district,
community_area,
fips,
substr(fips,-4,1) as block_group,
FROM vacant
UNION ALL
SELECT
type_of_service_request,
service_request_number,
creation_date,
completion_date,
julianday(completion_date) - julianday(creation_date) as days_to_complete,
street_address,
zip_code,
x_coordinate,
y_coordinate,
latitude,
longitude,
ward,
police_district,
community_area,
fips,
substr(fips,-4,1) as block_group
FROM alley
UNION ALL
SELECT
type_of_service_request,
service_request_number,
creation_date,
completion_date,
julianday(completion_date) - julianday(creation_date) as days_to_complete,
street_address,
zip_code,
x_coordinate,
y_coordinate,
latitude,
longitude,
ward,
police_district,
community_area,
'' as fips,
'' as block_group
FROM graffiti
'''

'''
WITH temp AS (
SELECT
substr(creation_date, 7, 4) || '-' || substr(creation_date, 1,2) || '-' || substr(creation_date, 4,2) as creation_date,
status,
substr(completion_date, 7, 4) || '-' || substr(completion_date, 1,2) || '-' || substr(completion_date, 4,2) as completion_date,
service_request_number,
type_of_service_request,
street_address,
zip_code,
x_coordinate,
y_coordinate,
ward,
police_district,
community_area,
latitude,
longitude,
location
FROM alley_fs
where creation_date like '%/2016' 
and (creation_date like '06/%' or 
     creation_date like '07/%' or 
     creation_date like'08/%')
)
INSERT INTO alley 
SELECT *,
get_fips(latitude, longitude)
FROM temp
;'''


'''
INSERT INTO graffiti
SELECT 
substr(creation_date, 7, 4) || '-' || substr(creation_date, 1,2) || '-' || substr(creation_date, 4,2) as creation_date,
status,
substr(completion_date, 7, 4) || '-' || substr(completion_date, 1,2) || '-' || substr(completion_date, 4,2) as completion_date,
service_request_number,
type_of_service_request,
surface_type,
graffiti_location,
street_address,
zip_code,
x_coordinate,
y_coordinate,
ward,
police_district,
community_area,
ssa,
latitude,
longitude,
location
FROM graffiti_fs
where creation_date like '%/2016' 
and (creation_date like '06/%' or 
     creation_date like '07/%' or 
     creation_date like'08/%')
'''


'''
WITH temp AS (
SELECT 
service_request_type,
service_request_number,
substr(date_service_request_received, 7, 4) || '-' || substr(date_service_request_received, 1,2) || '-' || substr(date_service_request_received, 4,2) as date_service_request_received,
location_of_building_on_lot,
is_bldg_dangerous_hazardous,
bldg_boarded,
is_bldg_open,
vacant_or_occupied,
vacant_due_to_fire,
people_on_property,
address_street_number,
address_street_direction,
address_street_name,
address_street_suffix,
zip_code,
x_coordinate,
y_coordinate,
ward,
police_district,
community_area,
latitude,
longitude,
location,
address_street_number || ' ' || address_street_direction || ' ' || address_street_name || ' ' || address_street_suffix as street_address
FROM vacant_fs
where date_service_request_received like '%/2016' 
and (date_service_request_received like '06/%' or 
     date_service_request_received like '07/%' or 
     date_service_request_received like'08/%')
and location != ''
)
INSERT INTO vacant 
SELECT *,
get_fips(latitude, longitude)
FROM temp
;'''


