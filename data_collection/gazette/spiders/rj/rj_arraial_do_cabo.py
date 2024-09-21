from datetime import date, datetime

from scrapy import Request
from scrapy.http.response.html import HtmlResponse

from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider


class RjArraialdoCabopider(BaseGazetteSpider):
    TERRITORY_ID = "3300258"

    name = "rj_arraial_do_cabo"
    allowed_domains = ["portal.arraial.rj.gov.br"]
    start_urls = ["https://portal.arraial.rj.gov.br/diarios_oficiais_web"]
    start_date = date(2019, 5, 7)

    def parse(self, response: HtmlResponse):
        for entry in response.css(".row .card.card-margin"):
            edition = entry.css("h5.card-title").re_first(r"(\d*) \/ \d{4}")
            file_url = entry.css(".widget-49-meeting-action.mt-2 a::attr(href)")
            publish_date = entry.css(".widget-49-date-day::text").extract_first()
            publish_date = datetime.strptime(publish_date, "%d %b %Y").date()

            if not self.start_date <= publish_date <= self.end_date:
                continue

            yield Gazette(
                date=publish_date,
                file_urls=[file_url.extract_first()],
                edition_number=edition,
                is_extra_edition=False,
                territory_id=self.TERRITORY_ID,
                power="executive",
            )

        if next_page := response.xpath('//a[contains(@rel, "next")]/@href'):
            yield Request(next_page.extract_first(), callback=self.parse)
