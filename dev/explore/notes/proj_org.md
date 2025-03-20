The package will consist of a few modules

BACK END
 - data - responsible for the downloading/preprocessing of game data
    - RAW - download the raw api results for dates
    - CLEAN - contains the first-pass cleaned RAW data, now tabular
      - flatten nested objects (white/black info)
      - extract moves + clock + opening code (ECO) from PGN string
      - get time control/ time_class / final position
      - metadata: game url, game datetime
      -
      - drop some unused columns
      - drop some unused rows (rules != chess)
    - PREPROC - transform columns to facilitate plots/analysis
      -

 - analysis - responsible for transforming clean data into plots
    - process the clean data to glean insights for the subsequent analysis
FRONT END
 - Get username from user
 - allow them to customise their analysis
 - present the plots


The data folder.
Naming convention:
{username}_{start_year_month}-{end_year_month}_raw/clean/proc#.pickle (pickle)
JammyNinja_2023_01-2023_12_raw.pickle
JammyNinja_2023_01-2023_12_clean.pickle
JammyNinja_2023_01_2023_12_proc.pickle
