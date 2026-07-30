#!/bin/bash
# Query Nominatim for each node location, with delay to respect rate limits
# Output: name | queried_lat,queried_lng | source_lat,source_lng

# Key nodes to verify
declare -A LOCS
LOCS["江西瑞金"]="瑞金"
LOCS["福建长汀"]="长汀"
LOCS["江西于都"]="于都"
LOCS["湖南通道"]="通道侗族自治县"
LOCS["贵州黎平"]="黎平"
LOCS["贵州遵义"]="遵义"
LOCS["云南威信（扎西镇）"]="威信县"
LOCS["贵州、四川、云南交界（赤水河一带）"]="赤水河"
LOCS["云南寻甸、禄劝（皎平渡）"]="皎平渡"
LOCS["四川石棉（安顺场）"]="安顺场"
LOCS["四川泸定"]="泸定"
LOCS["四川宝兴（夹金山）"]="夹金山"
LOCS["陕西吴起镇"]="吴起县"
LOCS["甘肃会宁"]="会宁县"

for name in "${!LOCS[@]}"; do
    query="${LOCS[$name]}"
    result=$(curl -s "https://nominatim.openstreetmap.org/search?q=$query&format=json&limit=1" -H "User-Agent: longmarch-map/1.0" --max-time 10 2>/dev/null)
    lat=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['lat'] if d else 'N/A')" 2>/dev/null)
    lon=$(echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['lon'] if d else 'N/A')" 2>/dev/null)
    echo "$name | $lat,$lon"
    sleep 1
done
