source rssreaderenv/bin/activate
python3.10 -m pip install -r requirements.txt
python3.10 rss_loader.py
python3.10 enricher.py
