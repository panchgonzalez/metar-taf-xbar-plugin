# METAR + TAF XBar plugin

## Setup
1. Download [xbar](xbarapp.com)

2. Clone repo
```
git clone git@github.com:panchgonzalez/metar-taf-xbar-plugin.git
cd metar-taf-xbar-plugin
```

3. Update Airport ICAO Code in the script `metar_taf.5m.py`
```
# ===== CONFIG =====
AIRPORT = "KDPA"   # ICAO code
TIMEOUT = 10
# ==================
```

4. Copy file to xbar plugin folder
```
cp metar_taf.5m.py ~/Library/Application\ Support/xbar/plugins
```

5. Make script executable
```
chmod +x ~/Library/Application\ Support/xbar/plugins/metar_taf.5m.py
```

6. Refresh all plugins

