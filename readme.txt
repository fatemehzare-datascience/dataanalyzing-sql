The data has been selected from a remote database by SQL code for Location, GPS and Battery tables.
For the location table, we removed location records outside the Saskatoon area, (52.058367, -106.7649138128) and (52.214608, -106.52225318),
and with a GPS accuracy greater than 100 meters.
Locations outside Saskatoon mostly indicate travels, which represents a few records of the data.
Although our dataset is composed by students of the U of S, we did not restrict the area to the U of S because some students might have
contacts outside the university.
For both location and WiFi table,  the records between October 6th of 2014 and
November 6th of 2014 are selected, which was the period of the SHED5 study. We had to filter the date since we
found records before the period of the study. We then removed participants from both tables who
had less than 50% of total possible battery records, which we considered insufficient to represent our
study. The number of total battery possible records is 9216, which is the number of total possible
Duty Cycles.
The filtered location and WiFi tables had 161,891 (52% less records than the original) and 2,525,661
(19% smaller) records, respectively, with 26 participants
After the filtering step, we aggregated the data by Duty Cycle and participant since each participant
can have more than one location or WiFi records in the same Duty Cycle. To simplify the aggregation
for different times in the same Duty Cycle, we rounded the time for each 5 minutes. For aggregating
the location table, we took the first time record and the average latitude and longitude values. For
the WiFi table, we took the maximum RSSI value, i.e., the closest WiFi router, with its corresponding
MAC address and time.
Afterwards, we stratified the location table, i.e., outdoor environment into contacts when the
euclidean distance between two participants is equal or less than the transmission range.
For WiFi records (indoor environment), we stratified the data into contacts when two participants
was using the same WiFi router (same MAC address) at the same time and at a specific Received Signal Strength Indication (RSSI).
The greater is the RSSI level, closer the participant is to the WiFi router.
