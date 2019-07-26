<table>
    <tr>
        <td>License</td>
        <td><img src='https://img.shields.io/pypi/l/ezscrape.svg'></td>
        <td>Version</td>
        <td><img src='https://img.shields.io/pypi/v/ezscrape.svg'></td>
    </tr>
    <tr>
        <td>Travis CI</td>
        <td><img src='https://travis-ci.org/ericziethen/ezscrape.svg?branch=master'></td>
        <td>Coverage</td>
        <td><img src='https://codecov.io/gh/ericziethen/ezscrape/branch/master/graph/badge.svg'></td>
    </tr>
    <tr>
        <td>Wheel</td>
        <td><img src='https://img.shields.io/pypi/wheel/ezscrape.svg'></td>
        <td>Implementation</td>
        <td><img src='https://img.shields.io/pypi/implementation/ezscrape.svg'></td>
    </tr>
    <tr>
        <td>Status</td>
        <td><img src='https://img.shields.io/pypi/status/ezscrape.svg'></td>
        <td>Downloads</td>
        <td><img src='https://img.shields.io/pypi/dm/ezscrape.svg'></td>
    </tr>
    <tr>
        <td>Supported versions</td>
        <td><img src='https://img.shields.io/pypi/pyversions/ezscrape.svg'></td>
    </tr>
</table>

# ezscrape

ezscrape provides a boilerplate for simple scraping tasks.

It provide generic access to scraping functionality without exposing the user directly the the underlying libraries used (e.g. requests, selenium) when using the scraping functionality.
The used scraper is chosen based on the specified config parameters and will prefer the most flexibe / least resource intensive ones if possible.

The exceptions of the underlying modules are handled and converted into the status of the result object.

# Setup Requirements
## Setup Chrome and Webdriver

For some websites selenium will be used for scraping (e.g. requests doesn't support javascript)

For that purpose the following environment variables need to be set otherwise an exception will be raised when the code is using selenium.

1. The Chrome Executable

    *CHROME_EXEC_PATH*

2. The Chrome Webdriver Executable

    *CHROME_WEBDRIVER_PATH*

# Usage

1. The basic concept of a simple scrape is
2. Create the Scrape Config with a Url
3. Optional - set additional parameters on the scrape config
4. Scrape with the given Config
5. Check the Return Object if the Scrape was succesfull
6. Get the HTML from the Return Object


## Scrape a simple HTML Page

~~~

import ezscrape.scraping.scraper as scraper
from ezscrape.scraping.core import ScrapeConfig
from ezscrape.scraping.core import ScrapeStatus

result = scraper.scrape_url(ScrapeConfig('http://www.website.com'))

if result.status == ScrapeStatus.SUCCESS:
    html = result.first_page.html
else:
    print(result.error_msg)

~~~

## Scrape a Page with Multiple Pages

~~~

import ezscrape.scraping.scraper as scraper
from ezscrape.scraping.core import ScrapeConfig
from ezscrape.scraping.core import WaitForXpathElem
from ezscrape.scraping.core import ScrapeStatus

config = ScrapeConfig('http://www.website.com')
# Add contition to wait until Element with "title='id'" is loaded"
config.wait_for_elem_list.append(WaitForXpathElem(R'''//a[@title='id']'''))

result = scraper.scrape_url(config)

for page in result:
    if page.status == ScrapeStatus.SUCCESS:
        html = page.html
    else:
        print(result.error_msg)
~~~

## Scrape a Page and wait until an Element is Loaded

~~~

import ezscrape.scraping.scraper as scraper
from ezscrape.scraping.core import ScrapeConfig
from ezscrape.scraping.core import WaitForXpathElem
from ezscrape.scraping.core import ScrapeStatus


config = ScrapeConfig('http://www.website.com')
# Add contition to wait until Element with "title='id'" is loaded"
config.wait_for_elem_list.append(WaitForXpathElem(R'''//a[@title='id']'''))

result = scraper.scrape_url(config)

if result.status == ScrapeStatus.SUCCESS:
    html = result.first_page.html
else:
    print(result.error_msg)

~~~

# Scrape Config

ezscrape.scraping.core.ScrapeConfig

The url is specified when creating the object.

~~~
from ezscrape.scraping.core import ScrapeConfig

config = ScrapeConfig('http://some-url.com') 
~~~

Additional parameters can be specified

| Option                          | Purpose                                  | Type                                     | Default           | Example Use Case                         |
|---------------------------------|------------------------------------------|------------------------------------------|-------------------|------------------------------------------|
| ScrapeConfig.url                | The URL used for the request             | str                                      | N/A               | Required for all Requests                |
| ScrapeConfig.request_timeout    | The timeout in seconds of the request    | long                                     | 15                | Wait longer before timeout in a slow Network environment. |
| ScrapeConfig.page_load_wait     | Time ti wait until a page is loaded completely before it times out | int                                      | 5.0               | Specify a longer time if the page loads dynamic elements slowly |
| ScrapeConfig.proxy_http         | HTTP Proxy to use                        | str                                      | N/A               | Send the request through an HTTP proxy (Proxy needs to support the Target protocol i.e. HTTP/HTTPS) |
| ScrapeConfig.proxy_https        | HTTPS Proxy to use                       | str                                      | N/A               | Send the request through an HTTPS proxy (Proxy needs to support the Target protocol i.e. HTTP/HTTPS) |
| ScrapeConfig.useragent          | Custom Useragent to use                  | str                                      | Internally Chosen | User want to scrape with a custom Useragent |
| ScrapeConfig.max_pages          | Maximum Pages to collect if "next_button" specifies  | int                                      | 15                | User only wants to return 3 Pages max even if more pages available |
| ScrapeConfig.next_button        | Add a button element that needs to be loaded and clicked for ultiple pages | ezscrape.scraping.core.WaitForPageElem<br><br>or one of the subtypes e.g.<br><br>ezscrape.scraping.core.WaitForXpathElem | N/A               | User wants to return multiple pages if the next page links are generated with Javascript |
| ScrapeConfig.wait_for_elem_list | A list of Elements that need to be loaded on the page before returning the scrape result | List of <br>ezscrape.scraping.core.WaitForPageElem<br><br>or one of the subtypes e.g.<br><br>ezscrape.scraping.core.WaitForXpathElem | N/A               | User is interested in multiple elements of a Javascript/Ajax page and needs to wait for all to load completely. |

# Scrape Status

The following statuses are supported in ezscrape.scraping.core.ScrapeStatus

| Status                   | Meaning                 |
|--------------------------|-------------------------|
| ScrapeStatus.SUCCESS     | Scrape Succesfull       |
| ScrapeStatus.TIMEOUT     | A timeout error occured |
| ScrapeStatus.PROXY_ERROR | A proxy error occured   |
| ScrapeStatus.ERROR       | A generic error occured |

For non Success cases, additional error details are given in the [ScrapeResult](#scrape-result) object

# Scrape Result

The following attributes are available in ezscrape.scraping.core.ScrapeResults

| Attribute              | Purpose                                  | Type                                |
|------------------------|------------------------------------------|-------------------------------------|
| ScrapeResult.url       | The url Scraped                          | str                                 |
| ScrapeResult.caller_ip | The caller IP.<br><br>This is not set for all cases. But where it is it should be reliable e.g. if Scraped through proxy, the proxy IP should be shown) | str                                 |
| ScrapeResult.status    | The overall status of the Scrape         | ezscrape.scraping.core.ScrapeStatus |
| ScrapeResult.error_msg | The error message if the result is not SUCCESS | str                                 |
| request_time_ms        | The combined scrape time of all pages scraped | float                               |
| first_page             | The ScrapePage scraped (first if multiple pages) | ezscrape.scraping.core.ScrapePage   |

# Scrape Page

The following attributes are available in ezscrape.scraping.core.ScrapePage

| Attribute       | Purpose                                  | Type                                |
|-----------------|------------------------------------------|-------------------------------------|
| html            | The HTML content scraped                 | str                                 |
| request_time_ms | the scrape duration for this page        | float                               |
| status          | The scrape status for this page<br><br>ScrapePage doesn't have it's own error message. For details check ScrapeResult.error_msg | ezscrape.scraping.core.ScrapeStatus |

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GPLv3](https://choosealicense.com/licenses/gpl-3.0/)

  [1]: # Scrape Result
  [2]: # Scrape Result
