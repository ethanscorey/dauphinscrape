import datetime
import os

BOT_NAME = "dauphinscrape"

SPIDER_MODULES = ["dauphinscrape.spiders"]
NEWSPIDER_MODULE = "dauphinscrape.spiders"
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 2
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

DUPEFILTER_DEBUG = True
COOKIES_DEBUG = True
LOG_LEVEL = "DEBUG"

EXTENSIONS = {
    "dauphinscrape.schedulelogger.SchedulerQueueLogger": 100,
}

# Dauphin-specific settings
DAUPHIN_INIT_FORMDATA = {
    "flow_action": "searchbyname",
    "quantity": "100",
    "searchtype": "PIN",
    "systemUser_includereleasedinmate": "N",
    "systemUser_includereleasedinmate2": "N",
    "systemUser_firstName": "",
    "systemUser_lastName": "",
    "systemUser_dateOfBirth": "",
    "releasedA": "checkbox",
    "identifierbox": "PIN",
    "identifier": "",
    "releasedB": "checkbox",
}
DAUPHIN_INIT_URL = "https://www.dauphinc.org:9443/IML"
DAUPHIN_ROW_XPATH = "//tr[@class='body']"
DAUPHIN_PERSON_REGEXES = {
    "name": r"Name:__+(?P<name>([A-Z-']+ *)+)__+",
    "sex": r"Sex:__+(?P<sex>[A-Z]+)__+",
    "dob": r"DOB:__+(?P<dob>\d{2}/\d{2}/\d{4})__+",
    "height": r"Height:__+(?P<height>\d+' \d+\")__+",
    "weight": r"Weight:__+(?P<weight>\d+)__+",
    "hair_color": r"Hair Color:__+(?P<hair_color>[A-Z]+)__+",
    "hair_length": r"Hair Length:__+(?P<hair_length>(?:[A-Z]+ ?)+)__+",
    "eye_color": r"Eye Color:__+(?P<eye_color>(?:[A-Z]+ ?)+)__+",
    "complexion": r"Complexion:__+(?P<complexion>(?:[A-Z]+ ?)+)__+",
    "booking_no": r"Booking #:__+(?P<booking_no>(?:\w|-)+)__+",
    "perm_id": r"Permanent ID #:__+(?P<perm_id>\d+)__+",
    "police_county_id": r"Police/County ID:__+(?P<police_county_id>(?:\w|-)+)__+",
    "race": r"Race:__+(?P<race>(?:[A-Z]+ ?)+)__+",
    "ethnicity": r"Ethnicity:__+(?P<ethnicity>(?:[A-Z]+ ?)+)__+",
    "marital_status": r"Marital Status:__+(?P<marital_status>(?:\w+ ?)+)__+",
    "citizen": r"Citizen:__+(?P<citizen>(?:[A-Z]+ ?)+)__+",
    "country_of_birth": r"Country of Birth:__+(?P<country_of_birth>(?:[A-Z]+ ?)+)__+",
    "curr_loc": r"Current Location:__+(?P<curr_loc>(?:[A-Z]+ ?)+)__+",
    "county": r"County:__+(?P<county>(?:[A-Z] ?)+)__+",
    "commit_date": r"Commitment Date:__+(?P<commit_date>\d{2}/\d{2}/\d{4})__+",
    "proj_release_date": r"Projected Release Date:__+(?P<proj_release_date>\d{2}/\d{2}/\d{4})__+",
    "bond_type": r"Bond Type:__+(?P<bond_type>(?:[A-Z]+ ?)+)__+",
    "bond_status": r"(?<!Marital )Status:__+(?P<bond_status>(?:\w+ ?)+)__+",
    "posted_by": r"Posted By:__+(?P<posted_by>(?:\w+ ?)+)__+",
    "post_date": r"Post Date:__+(?P<post_date>\d{2}-\d{2}-\d{4})__+",
    "bond_total": r"Grand Total:__+(?:Â¤)?(?P<bond_total>(?:\d{1,3},?)*\d{1,3}\.\d{2})__+",
}

# Export settings
BUCKET_NAME = os.getenv("SPIDER_EXPORT_BUCKET")
NOW = datetime.datetime.now().isoformat()
TODAY = datetime.date.today().isoformat()
LOGFILE_KEY = f"logs/log-{NOW}.log"
FEEDS = {
    f"s3://{BUCKET_NAME}/charges/charges-latest.csv": {
        "format": "csv",
        "encoding": "utf8",
        "overwrite": True,
    },
    f"s3://{BUCKET_NAME}/charges/charges-{TODAY}.csv": {
        "format": "csv",
        "encoding": "utf8",
        "overwrite": True,
    },
}
