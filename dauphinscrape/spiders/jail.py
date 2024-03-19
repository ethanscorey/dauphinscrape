import re
import time
import urllib.parse
from collections.abc import Iterator
from typing import Any

import scrapy

from dauphinscrape.items import ChargeItem
from dauphinscrape.utils import get_regex


class JailSpider(scrapy.Spider):
    name = "jail"

    def start_requests(self) -> Iterator[scrapy.FormRequest]:
        """Send initial POST request to get first page of search results.

        Returns: A generator with a single scrapy FormRequest
        """
        self.logger.info(self.settings.get("DEPTH_LIMIT"))
        formdata = self.settings.getdict("DAUPHIN_INIT_FORMDATA")
        yield scrapy.FormRequest(
            url=self.settings.get("DAUPHIN_INIT_URL"),
            formdata=formdata,
            callback=self.parse_results,
            errback=self.handle_error,
        )

    def parse_results(
        self, response: scrapy.http.Response
    ) -> Iterator[scrapy.FormRequest]:
        """Parse initial page of results and make requests.

        Returns: generator[scrapy.FormRequest] FormRequests for each
            person listed in the initial results
        """
        rows = response.xpath(self.settings.get("DAUPHIN_ROW_XPATH"))
        row_count = response.xpath("//font[contains(text(), 'Showing')]/text()").get()
        start, end = re.findall(r"\d+", row_count)[1:3]
        if int(start) < int(end):
            self.logger.info("Getting next page...")
            request = scrapy.FormRequest(
                url=response.url,
                formdata={"flow_action": "next", "currentStart": start},
                callback=self.parse_results,
                errback=self.handle_error,
            )
            self.logger.info(request.body)
            yield request
        for row in rows:
            yield self.get_person_data(row)

    def get_person_data(self, row: scrapy.Selector) -> scrapy.FormRequest:
        """Request the person detail page for the provided row.

        Params:
        - row: A row from the results table
        Returns: scrapy.FormRequest A POST request to get the detail page
        """
        person_id, image_id = row.xpath(".//a[contains(@href, 'submitInmate')]")[0].re(
            "\d+"
        )
        return scrapy.FormRequest(
            url=self.settings.get("DAUPHIN_INIT_URL"),
            formdata={
                "flow_action": "edit",
                "sysID": person_id,
                "imgSysID": image_id,
            },
            callback=self.parse_person_data,
            cb_kwargs={"image_id": image_id, "person_id": person_id},
            errback=self.handle_error,
        )

    def parse_person_data(self, response: scrapy.http.Response, image_id: str, person_id: str) -> Iterator[ChargeItem]:
        """Extract data for the person detail page.
        Params:
        - response: scrapy.http.Response The response for the person
            detail page
        - image_id: str The image ID for the mugshot.
        - person_id: str The ID for the person.
        Returns: Iterator[ChargeItem] All charges for the requested person.
        """
        self.logger.info(f"Scraped {response.request.body}")
        text = "__".join(
            [i.strip() for i in response.xpath("//text()").extract() if i.strip()]
        )
        regexes: dict[str, str] = self.settings.getdict("DAUPHIN_PERSON_REGEXES")
        person_data = {
            field: get_regex(pattern, text, [field])
            for (field, pattern) in regexes.items()
        }
        person_data["image_id"] = image_id
        person_data["person_id"] = person_id
        if not any(person_data.values()):
            self.logger.warning("No person data found -- are you sure this was a valid response?")
        for charge in self.parse_charges(response, person_data):
            yield charge

    def handle_error(self, error):
        self.logger.error(error)

    def parse_charges(
        self, response: scrapy.http.Response, person_data: dict[str, Any]
    ) -> list[ChargeItem]:
        """Extract charges for the person detail page."
        Params:
        - response: scrapy.http.Response The response for the person
            detail page
        Returns: list[ChargeItem]
        """
        charges: list[ChargeItem] = []
        rows = response.xpath("//tr[not(@class) and count(./td) = 6]")
        self.logger.info(f"Row count: {len(rows)}")
        for row in rows:
            self.logger.debug(row.xpath("./td").extract())
            case_no, offense_date, code, description, grade, degree = row.xpath("./td")
            charges.append(
                ChargeItem(
                    case_no=case_no.xpath("./text()").get(),
                    offense_date=offense_date.xpath("./text()").get(),
                    code=code.xpath("./text()").get(),
                    description=description.xpath("./text()").get(),
                    grade=grade.xpath("./text()").get(),
                    degree=degree.xpath("./text()").get(),
                    scrape_time=time.ctime(),
                    **person_data,
                )
            )
        return charges
