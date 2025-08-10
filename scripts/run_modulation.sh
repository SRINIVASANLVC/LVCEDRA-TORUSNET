#!/bin/bash

# echo "📄 Displaying bodies.csv:"
# cat templates/bodies.csv
# echo ""

# echo "📄 Displaying modulation_zones.csv:"
# cat templates/modulation_zones.csv
# echo ""

# echo "📄 Displaying utc_Texas.csv:"
# cat data/regions/NorthAmerica/USA/Texas/utc_Texas.csv
# echo ""

# echo "📄 Displaying utc_Texas.csv (filtered for Dallas):"
# grep -i "^Dallas" data/regions/NorthAmerica/USA/Texas/utc_Texas.csv

# echo "🚀 Running modulation script for Texas..."
# python3 modules/createderived/modulate_city.py data/regions/NorthAmerica/USA/Texas/utc_Texas.csv

# echo "🚀 Running modulation script for Jiva..."
# python3 modules/createderived/modulate_Jiva.py data/jiva/utc_Jiva.csv --name Srinivasan

echo "🚀 Running modulation script for Jiva..."
python3 modules/createderived/modulate_Jiva.py data/jiva/utc_Jiva.csv

# echo "🚀 Running modulation script for Dallas..."
# python modules/createderived/modulate_city.py data/regions/NorthAmerica/USA/Texas/utc_Texas.csv --city Dallas