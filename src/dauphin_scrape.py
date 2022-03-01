from collections.abc import Iterator
from dataclasses import asdict
import datetime
import json
import logging
import re
import sys
import time
from typing import Union, cast

from bs4 import BeautifulSoup
from bs4.element import Tag
import requests

from .models import ChargeData, PersonData
from .regexes import (
    ALL_CAPS,
    ALL_CAPS_PHRASE,
    DATE,
    DOLLAR_VAL,
    HEIGHT,
    ID_NO,
    NUM,
    PHRASE,
)


log_format = "%(name)s: %(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(stream=sys.stdout, format=log_format, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    URL = "https://www.dauphinc.org:9443/IML"
    outfile = f"output{datetime.datetime.now()}.jsonl"
    with requests.Session() as sess:
        init_data = get_initial_data(sess, URL)
        parse_rows(sess, URL, init_data, outfile)
        time.sleep(0.5)
        for data in get_remainder_data(sess, URL):
            parse_rows(sess, URL, data, outfile)


def get_initial_data(sess: requests.Session, url: str) -> list[Tag]:
    """Get the first page of search results."""
    INIT_DATA = {
        "flow_action": "searchbyname",
        "quantity": 100,
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
    resp = sess.post(url, data=INIT_DATA)
    logger.debug(resp)
    resp.raise_for_status()
    soup = get_soup(resp)
    return soup("tr", attrs={"class": "body"})


def get_remainder_data(
    sess: requests.Session, url: str
) -> Iterator[list[Tag]]:
    """Yield responses for remaining data until last page reached."""
    assert sess.cookies  # complain if no cookies set
    logger.debug(sess.cookies)
    row_count = 30
    curr_start = 31
    while row_count == 30:
        resp = sess.post(
            url, data={"flow_action": "next", "currentStart": curr_start}
        )
        logger.debug(resp)
        resp.raise_for_status()
        soup = get_soup(resp)
        rows = soup("tr", attrs={"class": "body"})
        n_rows = len(rows)
        row_count = n_rows
        curr_start += n_rows
        time.sleep(0.5)
        yield rows


def get_person_id(row: Tag) -> list[str]:
    """Extract data needed to get person details."""
    on_click = row.attrs.get("onclick", "")
    matches = re.findall(f"[0-9]{NUM}", on_click)
    logger.debug(matches)
    if len(matches) == 2:
        return matches
    return []


def parse_rows(
    sess: requests.Session, url: str, rows: list[Tag], outfile: str
) -> None:
    """Parse rows and get person data."""
    for row in rows:
        time.sleep(0.5)
        person_id = get_person_id(row)
        if person_id:
            sys_id, img_sys_id = person_id
            with open(outfile, "a") as outfile_handle:
                outfile_handle.write(
                    json.dumps(
                        asdict(get_person_data(sess, url, sys_id, img_sys_id))
                    )
                    + "\n"
                )


def get_person_data(
    sess: requests.Session, url: str, sys_id: str, img_sys_id: str
) -> PersonData:
    """Get data for individual person in the jail DB."""
    resp = sess.post(
        url,
        data={"flow_action": "edit", "sysID": sys_id, "imgSysID": img_sys_id},
    )
    logger.debug(resp)
    resp.raise_for_status()
    soup = get_soup(resp)
    soup_text = soup.get_text()
    bond_info = cast(
        Tag,
        soup.find(
            lambda tag: (tag.name == "table")
            and ("Bond Information" in tag.get_text())
        ),
    )
    bond_text = bond_info.get_text() if bond_info is not None else ""
    charge_info = cast(
        Tag,
        soup.find(
            lambda tag: (tag.name == "table")
            and ("Charge Information" in tag.get_text())
        ),
    )
    person = PersonData(
        name=get_field(
            "Name", f"(?P<name>{ALL_CAPS_PHRASE})", soup_text, ["name"]
        ),
        sex=get_field("Sex", f"(?P<sex>{ALL_CAPS})", soup_text, ["sex"]),
        dob=get_field("DOB", f"(?P<dob>{DATE})", soup_text, ["dob"]),
        height=get_field(
            "Height", f"(?P<height>{HEIGHT})", soup_text, ["height"]
        ),
        weight=get_field(
            "Weight", f"(?P<weight>{NUM})", soup_text, ["weight"]
        ),
        hair_color=get_field(
            "Hair Color",
            f"(?P<hair_color>{ALL_CAPS})",
            soup_text,
            ["hair_color"],
        ),
        hair_length=get_field(
            "Hair Length",
            f"(?P<hair_length>{ALL_CAPS_PHRASE})",
            soup_text,
            ["hair_length"],
        ),
        eye_color=get_field(
            "Eye Color",
            f"(?P<eye_color>{ALL_CAPS_PHRASE})",
            soup_text,
            ["eye_color"],
        ),
        complexion=get_field(
            "Complexion",
            f"(?P<complexion>{ALL_CAPS_PHRASE})",
            soup_text,
            ["complexion"],
        ),
        booking_no=get_field(
            "Booking #", f"(?P<booking_no>{ID_NO})", soup_text, ["booking_no"]
        ),
        perm_id=get_field(
            "Permanent ID #", f"(?P<perm_id>{NUM})", soup_text, ["perm_id"]
        ),
        police_county_id=get_field(
            "Police/County ID",
            f"(?P<police_county_id>{ID_NO})",
            soup_text,
            ["police_county_id"],
        ),
        race=get_field(
            "Race", f"(?P<race>{ALL_CAPS_PHRASE})", soup_text, ["race"]
        ),
        ethnicity=get_field(
            "Ethnicity",
            f"(?P<ethnicity>{ALL_CAPS_PHRASE})",
            soup_text,
            ["ethnicity"],
        ),
        marital_status=get_field(
            "Marital Status",
            f"(?P<marital_status>{PHRASE})",
            soup_text,
            ["marital_status"],
        ),
        citizen=get_field(
            "Citizen",
            f"(?P<citizen>{ALL_CAPS_PHRASE})",
            soup_text,
            ["citizen"],
        ),
        country_of_birth=get_field(
            "Country of Birth",
            f"(?P<cob>{ALL_CAPS_PHRASE})",
            soup_text,
            ["cob"],
        ),
        curr_loc=get_field(
            "Current Location",
            f"(?P<curr_loc>{ALL_CAPS_PHRASE})",
            soup_text,
            ["curr_loc"],
        ),
        county=get_field(
            "County", f"(?P<county>{ALL_CAPS_PHRASE})", soup_text, ["county"]
        ),
        commit_date=get_field(
            "Commitment Date",
            f"(?P<commit_date>{DATE})",
            soup_text,
            ["commit_date"],
        ),
        proj_release_date=get_field(
            "Projected Release Date",
            f"(?P<proj_release_date>{DATE})",
            soup_text,
            ["proj_release_date"],
        ),
        bond_type=get_field(
            "Bond Type",
            f"(?P<bond_type>{ALL_CAPS_PHRASE})",
            bond_text,
            ["bond_type"],
        ),
        bond_status=get_field(
            "Status", f"(?P<status>{PHRASE})", bond_text, ["status"]
        ),
        posted_by=get_field(
            "Posted By", f"(?P<posted_by>{PHRASE})", bond_text, ["posted_by"]
        ),
        post_date=get_field(
            "Post Date", f"(?P<post_date>{DATE})", bond_text, ["post_date"]
        ),
        bond_total=get_field(
            "Grand Total",
            f"(?P<bond_total>{DOLLAR_VAL})",
            bond_text,
            ["bond_total"],
        ),
        charges=get_charges(charge_info),
    )
    logger.debug(person)
    return person


def get_charges(soup: Tag) -> list[ChargeData]:
    """Extract charge data from Charge Information table."""
    if soup is None:
        return []
    charge_rows = soup(
        lambda tag: (tag.name == "tr") and not tag.attrs.get("class")
    )
    out = []
    for row in charge_rows:
        logger.debug(row)
        if len(row("td")) != 6:
            continue
        case_no, offense_date, code, description, grade, degree = row("td")
        charge_data = ChargeData(
            case_no=case_no.get_text(),
            offense_date=offense_date.get_text(),
            code=code.get_text(),
            description=description.get_text(),
            grade=grade.get_text(),
            degree=degree.get_text(),
        )
        logger.debug(charge_data)
        out.append(charge_data)
    return out


def get_re(pattern: str, text: str, groups: list) -> str:
    """Get matching expression, if it exists, or return empty string."""
    match = re.search(pattern, text)
    if match:
        logger.debug(match)
        return "".join(match.group(*groups))
    logger.debug(f"No match for {pattern}")
    return ""


def get_field(
    field_name: str, pattern: str, text: str, groups: list[Union[list, str]]
) -> str:
    """Extract field from text."""
    return get_re(f"{field_name}:\n{pattern}", text, groups).strip()


def get_soup(
    resp: requests.Response, parser: str = "html.parser"
) -> BeautifulSoup:
    return BeautifulSoup(resp.content, parser)


if __name__ == "__main__":
    main()
