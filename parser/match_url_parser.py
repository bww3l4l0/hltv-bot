from datetime import date, timedelta
from typing import Literal
from parser.hltv_parser_extended_data import make_driver
from undetected_chromedriver import By, Chrome, WebElement


def __get_match_urls_by_date(driver: Chrome, day: Literal['today', 'tomorrow']) -> list[WebElement]:
    matches = []
    if day not in ['today', 'tomorrow']:
        driver.quit()
        raise ValueError('некоректная дата')

    target_date = date.today() if day == 'today' else date.today() + timedelta(days=1)
    for element in driver.find_elements(By.CSS_SELECTOR,
                                        '.upcomingMatchesSection'):

        header = element.find_element(By.CSS_SELECTOR,
                                      '.matchDayHeadline')
        day = header.text.split(' ')[-1]
        if date.fromisoformat(day) == target_date:
            matches = element.find_elements(By.CSS_SELECTOR,
                                            'a.match.a-reset')
    result = list(map(lambda foo: foo.get_attribute('href'), matches))
    driver.quit()
    return result


def __get_live_match_urls(driver: Chrome) -> list[str]:
    result = list(map(lambda e: e.get_attribute('href'),
                      driver.find_elements(By.CSS_SELECTOR,
                                           '.liveMatchesContainer a.match.a-reset')))

    driver.quit()
    return result


def fetch_match_urls(time: Literal['live', 'today', 'tomorrow']) -> list[WebElement]:
    '''
    возвращает ссылки на матчи(лайв, сегодня, завтра)
    '''
    driver = make_driver()
    url = 'https://www.hltv.org/matches'
    driver.get(url)
    if time == 'live':
        return __get_live_match_urls(driver)
    return __get_match_urls_by_date(driver, time)

# def get_match_urls(target_date: str = 'today'
#                    ) -> list[str]:
#     driver = make_driver()
#     url = 'https://www.hltv.org/matches'
#     driver.get(url)

#     if target_date == 'live':
#         result = list(map(lambda e: e.get_attribute('href'),
#                           driver.find_elements(By.CSS_SELECTOR,
#                                                '.liveMatchesContainer a.match.a-reset')))

#     if target_date == 'today':
#         matches = []
#         for element in driver.find_elements(By.CSS_SELECTOR,
#                                             '.upcomingMatchesSection'):
#             header = element.find_element(By.CSS_SELECTOR,
#                                           '.matchDayHeadline')
#             day = header.text.split(' ')[-1]
#             if date.fromisoformat(day) == date.today():
#                 matches = element.find_elements(By.CSS_SELECTOR,
#                                                 'a.match.a-reset')

#         result = list(map(lambda foo: foo.get_attribute('href'), matches))

#     if target_date == 'tomorrow':
#         matches = []
#         for element in driver.find_elements(By.CSS_SELECTOR,
#                                             '.upcomingMatchesSection'):
#             header = element.find_element(By.CSS_SELECTOR,
#                                           '.matchDayHeadline')
#             day = header.text.split(' ')[-1]
#             if date.fromisoformat(day) == date.today() + timedelta(days=1):
#                 matches = element.find_elements(By.CSS_SELECTOR,
#                                                 'a.match.a-reset')

#         result = list(map(lambda foo: foo.get_attribute('href'), matches))
#     driver.quit()
#     return result
