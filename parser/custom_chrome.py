from time import sleep
from datetime import date, timedelta
from typing import Literal
from undetected_chromedriver import Chrome, ChromeOptions, By, WebElement
from pyvirtualdisplay import Display
from parser.hltv_parser_extended_data import (
    get,
    get_team_names,
    get_winstreaks,
    get_face_to_face_stats,
    get_map_stats,
    get_result,
    get_countries,
    get_rank,
    is_lan,
    get_date,
    get_player_links,
    get_player_full_stats
    )

from settings import settings


class CustomChrome(Chrome):

    def __init__(self,
                 proxy: str = None,
                 timeout: int = 60,
                 wait_time: int = 30,
                 browser_executable_path: str = None,
                 driver_executable_path: str = None) -> None:

        self.__display = Display()

        self.__display.start()

        options = ChromeOptions()
        options.add_argument('--password-store=basic')
        # options.page_load_strategy = 'none'
        options.page_load_strategy = 'eager'
        if proxy is not None:
            options.add_argument(f"--load-extension={proxy}")

        super().__init__(options=options,
                         browser_executable_path=browser_executable_path,
                         driver_executable_path=driver_executable_path
                         )

        self.set_page_load_timeout(timeout)
        self.implicitly_wait(wait_time)

    def __del__(self) -> None:
        super().__del__()
        self.__display.stop()
        del self.__display


# def make_driver(proxy: str = None,
#                 timeout: int = 60,
#                 wait_time: int = 30) -> Chrome:

#     options = ChromeOptions()
#     options.add_argument('--password-store=basic')
#     # options.page_load_strategy = 'none'
#     options.page_load_strategy = 'eager'
#     if proxy is not None:
#         options.add_argument(f"--load-extension={proxy}")
#     driver = CustomChrome(options=options,
#                           browser_executable_path='/usr/bin/google-chrome',
#                           # driver_executable_path='/home/sasha/Documents/chromedriver'
#                           driver_executable_path='./chromedriver'
#                           )

#     # driver.minimize_window()
#     driver.set_page_load_timeout(timeout)
#     driver.implicitly_wait(wait_time)
#     sleep(2)
#     return driver


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


def fetch_match_urls(time: Literal['live', 'today', 'tomorrow']) -> list[str]:
    '''
    возвращает ссылки на матчи(лайв, сегодня, завтра)
    '''
    driver = CustomChrome(browser_executable_path=settings.CHROME_EXECUTABLE_PATH,
                          driver_executable_path=settings.DRIVER_EXECUTABLE_PATH)
    url = 'https://www.hltv.org/matches'
    driver.get(url)
    if time == 'live':
        return __get_live_match_urls(driver)
    return __get_match_urls_by_date(driver, time)


def process_match(url: str, proxy: str = None,
                  history: bool = False,
                  extended: bool = False
                  ) -> dict[str, any]:
    
    # display = Display(size=(1920, 1080))

    # display.start()

    # driver = make_driver(proxy, 30, 15)

    driver = CustomChrome(proxy, 30, 15,
                          browser_executable_path=settings.CHROME_EXECUTABLE_PATH,
                          driver_executable_path=settings.DRIVER_EXECUTABLE_PATH
                          )

    get(driver, url, 'match')

    res = {}

    res['url'] = driver.current_url

    try:
        # названия команд
        res.update(get_team_names(driver))

        if extended:
            # винстрики
            res.update(get_winstreaks(driver))
            # очные встречи
            res.update(get_face_to_face_stats(driver))
            # статистика по картам
            res.update(get_map_stats(driver))

        if history:
            try:
                res.update(get_result(driver))
            except Exception as e:
                driver.quit()
                raise e

        res.update(get_countries(driver))

        # лан или онлайн
        res['lan'] = int(is_lan(driver))

        try:
            res['team1_rank'] = int(get_rank(driver, 1))
        except Exception:
            res['team1_rank'] = 1001

        try:
            res['team2_rank'] = int(get_rank(driver, 2))
        except Exception:
            res['team2_rank'] = 1001

        res['date'] = str(get_date(driver))

        team1_players = get_player_links(driver, 1)
        team2_players = get_player_links(driver, 2)

        if not team1_players:  # если нету для одной команды значит нету и для второй а значит что матч еще не сыгран
            team1_url = driver.find_element(By.CSS_SELECTOR,
                                            '.team1-gradient a')\
                                                .get_attribute('href')

            team2_url = driver.find_element(By.CSS_SELECTOR,
                                            '.team2-gradient a').get_attribute('href')

            # driver.get(team1_url)
            get(driver, team1_url, 'team')
            team1_players = list(map(lambda x: x.get_attribute('href'),
                                     driver.find_elements(By.CSS_SELECTOR,
                                                          '.bodyshot-team.g-grid a')))
            # driver.get(team2_url)
            get(driver, team2_url, 'team')
            team2_players = list(map(lambda x: x.get_attribute('href'),
                                     driver.find_elements(By.CSS_SELECTOR,
                                                          '.bodyshot-team.g-grid a')))

            if not team1_players:
                raise ValueError('невозможно извлечь ссылки на профили игроков')

            if not team2_players:
                raise ValueError('невозможно извлечь ссылки на профили игроков')

    except Exception as e:
        driver.quit()
        # display.stop()
        raise e

    try:
        for number, player_url in enumerate(team1_players):
            res.update(get_player_full_stats(driver,
                                             player_url,
                                             res['date'],
                                             1,
                                             number,
                                             26,
                                             ' '))

        for number, player_url in enumerate(team2_players):
            res.update(get_player_full_stats(driver,
                                             player_url,
                                             res['date'],
                                             2,
                                             number,
                                             26,
                                             ' '))
    except Exception as e:
        raise e
    finally:
        driver.quit()
        # display.stop()

    return res


if __name__ == '__main__':
    url = 'https://www.hltv.org/matches/2375442/zero-tenacity-vs-sinners-yalla-compass-summer-2024'
    res = process_match(url)
    print(res)
