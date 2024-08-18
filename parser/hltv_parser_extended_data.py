import re
import pandas as pd
import resource
from undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from time import sleep
from datetime import date, timedelta, datetime
from multiprocessing import Pool, Manager
from random import sample
from selenium.common.exceptions import (TimeoutException,
                                        NoSuchElementException)
from random import choice
from typing import Literal

soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
resource.setrlimit(resource.RLIMIT_NOFILE, (hard, hard))


# Check and close cookie popup
# работает неправильно тк окно всегда есть
def check_popup(driver: Chrome) -> bool:
    if len(driver.find_elements(By.CSS_SELECTOR,
                                '.CybotCookiebotDialogContentWrapper')) != 0:
        return True
    return False


def close_popup(driver: Chrome) -> None:
    driver.find_element(By.CSS_SELECTOR,
                        '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll').click()
    '''actor = ActionChains(driver)
    try:
        actor.move_to_element(driver.find_element(By.CSS_SELECTOR,'#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll')).click().perform()
        return
    except:
        return'''


def make_driver(proxy: str = None,
                timeout: int = 60, 
                wait_time: int = 30) -> Chrome:

    options = ChromeOptions()
    options.add_argument('--password-store=basic')
    # options.page_load_strategy = 'none'
    options.page_load_strategy = 'eager'
    if proxy is not None:
        options.add_argument(f"--load-extension={proxy}")
    driver = Chrome(options=options,
                    browser_executable_path='/usr/bin/google-chrome',
                    # driver_executable_path='/home/sasha/Documents/chromedriver'
                    driver_executable_path='./chromedriver'
                    )
    driver.minimize_window()
    driver.set_page_load_timeout(timeout)
    driver.implicitly_wait(wait_time)
    sleep(2)
    return driver


def get_player_recent_statistics(basic_url, team, number, match_date, proxy):
    driver = make_driver(proxy)
    yesterday = date.fromisoformat(match_date) - timedelta(days=1)
    start_date = yesterday - timedelta(weeks=12)

    while True:
        try:
            driver.get(basic_url)
            url = driver.find_element(By.CSS_SELECTOR, 'a.moreButton').get_attribute('href')
            url = url + f'?startDate={start_date}&endDate={yesterday}'
            driver.get(url)
            driver.find_element(By.TAG_NAME, 'body')
            driver.find_element(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')
        except TimeoutException:
            # traceback.print_exc()
            continue
        except NoSuchElementException:
            # traceback.print_exc()
            continue
        except Exception as e:
            # traceback.print_exc()
            print(str(e))
            if ('ERR_PROXY_CONNECTION_FAILED' in str(e) or
                    'ERR_CONNECTION_RESET' in str(e)):
                # driver.quit()
                # driver = make_driver(proxy)
                continue
            driver.quit()
            raise e
        else:
            break

    try:

        res = {}

        res[f't{team}p{number}_recent_rating'] = \
            float(driver.find_elements(By.CSS_SELECTOR,
                                       '.summaryStatBreakdownDataValue')[0].text)
        res[f't{team}p{number}_recent_dpr'] = \
            float(driver.find_elements(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')[1].text)
        res[f't{team}p{number}_recent_kast'] = \
            float(re.findall("\d+\.\d+",
                             driver.find_elements(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')[2].text)[0])
        res[f't{team}p{number}_recent_impact'] = \
            float(driver.find_elements(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')[3].text)
        res[f't{team}p{number}_recent_adr'] = \
            float(driver.find_elements(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')[4].text)
        res[f't{team}p{number}_recent_kpr'] = \
            float(driver.find_elements(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')[5].text)
        # age

    except Exception as e:
        raise e
    finally:
        # sleep(60)
        driver.quit()

    driver.quit()
    return res


def get_player_full_statistics(basic_url, team, number, match_date, proxy):
    driver = make_driver(proxy)
    yesterday = date.fromisoformat(match_date) - timedelta(days=1)
    start_date = '2012-01-01'

    while True:
        try:
            driver.get(basic_url)
            url = (driver.find_element(By.CSS_SELECTOR, 'a.moreButton')
                   .get_attribute('href'))
            url = url + f'?startDate={start_date}&endDate={yesterday}'
            driver.get(url)
            driver.find_element(By.TAG_NAME, 'body')
            driver.find_element(By.CSS_SELECTOR,
                                '.summaryStatBreakdownDataValue')
        except TimeoutException:
            # traceback.print_exc()
            continue
        except NoSuchElementException:
            # traceback.print_exc()
            continue
        except Exception as e:
            # traceback.print_exc()
            print(str(e))
            if ('ERR_PROXY_CONNECTION_FAILED' in str(e) or
                    'ERR_CONNECTION_RESET' in str(e)):
                # driver.quit()
                # driver = make_driver(proxy)
                continue
            driver.quit()
            raise e
        else:
            break

    try:

        res = {}

        res[f't{team}p{number}_rating'] = float(driver.find_elements(By.CSS_SELECTOR,
                                                                     '.summaryStatBreakdownDataValue')[0].text)
        res[f't{team}p{number}_dpr'] = float(driver.find_elements(By.CSS_SELECTOR,
                                                                  '.summaryStatBreakdownDataValue')[1].text)
        res[f't{team}p{number}_kast'] = \
            float(re.findall("\d+\.\d+", driver.find_elements(By.CSS_SELECTOR,
                                                              '.summaryStatBreakdownDataValue')[2].text)[0])

        res[f't{team}p{number}_impact'] = float(driver.find_elements(By.CSS_SELECTOR,
                                                                     '.summaryStatBreakdownDataValue')[3].text)

        res[f't{team}p{number}_adr'] = float(driver.find_elements(By.CSS_SELECTOR,
                                                                  '.summaryStatBreakdownDataValue')[4].text)

        res[f't{team}p{number}_kpr'] = float(driver.find_elements(By.CSS_SELECTOR,
                                                                  '.summaryStatBreakdownDataValue')[5].text)

        res[f't{team}p{number}_country'] = \
            driver.find_element(By.CSS_SELECTOR, 'div.summaryRealname.text-ellipsis img.flag').get_attribute('title')
        # age
        try:
            res[f't{team}p{number}_age'] = int(re.findall(r'\d+',
                                                          driver.find_element(By.CSS_SELECTOR,
                                                                              'div.summaryPlayerAge').text)[0])
        except IndexError:
            res[f't{team}p{number}_age'] = 0

    except Exception as e:
        raise e
    finally:
        # sleep(60)
        driver.quit()

    driver.quit()
    return res


def get_player_urls(url):
    driver = make_driver()

    while True:
        try:
            driver.get(url)
            driver.find_element(By.TAG_NAME, 'body')
            driver.find_element(By.CSS_SELECTOR, 'a.col-custom')
        except TimeoutException:
            continue
        except NoSuchElementException:
            continue
        except Exception as e:
            print(str(e))
            if ('ERR_PROXY_CONNECTION_FAILED' in str(e) 
                    or 'ERR_CONNECTION_RESET' in str(e)):
                # driver.quit()
                # driver = make_driver()
                continue
            driver.quit()
            raise e
        else:
            break

    res = []
    for e in driver.find_elements(By.CSS_SELECTOR, 'a.col-custom'):
        res.append(e.get_attribute('href'))
    driver.quit()
    return res


def extract_data(driver, url, team, number):
    res = {}
    while True:
        try:
            driver.get(url)
            driver.find_element(By.TAG_NAME, 'body')
            driver.find_element(By.CSS_SELECTOR,
                                '.summaryStatBreakdownDataValue')
        except TimeoutException:
            # traceback.print_exc()
            continue
        except NoSuchElementException:
            # traceback.print_exc()
            continue
        except Exception as e:
            # traceback.print_exc()
            print(str(e))
            if ('ERR_PROXY_CONNECTION_FAILED' in str(e) or
                    'ERR_CONNECTION_RESET' in str(e)):
                # driver.quit()
                # driver = make_driver(proxy)
                continue
            driver.quit()
            raise e
        else:
            break

    res[f't{team}p{number}_rating'] = \
        float(driver.find_elements(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')[0].text)

    res[f't{team}p{number}_dpr'] = \
        float(driver.find_elements(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')[1].text)

    res[f't{team}p{number}_kast'] = \
        float(re.findall("\d+\.\d+", driver.find_elements(By.CSS_SELECTOR,
                                                          '.summaryStatBreakdownDataValue')[2].text)[0])

    res[f't{team}p{number}_impact'] = \
        float(driver.find_elements(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')[3].text)

    res[f't{team}p{number}_adr'] = \
        float(driver.find_elements(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')[4].text)

    res[f't{team}p{number}_kpr'] = \
        float(driver.find_elements(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')[5].text)

    res[f't{team}p{number}_country'] = \
        driver.find_element(By.CSS_SELECTOR, 'div.summaryRealname.text-ellipsis img.flag').get_attribute('title')
    # age
    try:
        res[f't{team}p{number}_age'] = int(re.findall(r'\d+', 
                                                      driver.find_element(By.CSS_SELECTOR,
                                                                          'div.summaryPlayerAge').text)[0])
    except IndexError:
        res[f't{team}p{number}_age'] = 0

    while True:
        try:
            driver.get(url)
            driver.find_element(By.TAG_NAME, 'body')
            driver.find_element(By.CSS_SELECTOR,
                                '.summaryStatBreakdownDataValue')
        except TimeoutException:
            # traceback.print_exc()
            continue
        except NoSuchElementException:
            # traceback.print_exc()
            continue
        except Exception as e:
            # traceback.print_exc()
            print(str(e))
            if ('ERR_PROXY_CONNECTION_FAILED' in str(e) or
                    'ERR_CONNECTION_RESET' in str(e)):
                # driver.quit()
                # driver = make_driver(proxy)
                continue
            driver.quit()
            raise e
        else:
            break

    res[f't{team}p{number}_recent_rating'] = \
        float(driver.find_elements(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')[0].text)

    res[f't{team}p{number}_recent_dpr'] = \
        float(driver.find_elements(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')[1].text)

    res[f't{team}p{number}_recent_kast'] = \
        float(re.findall("\d+\.\d+", driver.find_elements(By.CSS_SELECTOR,
                                                          '.summaryStatBreakdownDataValue')[2].text)[0])

    res[f't{team}p{number}_recent_impact'] = \
        float(driver.find_elements(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')[3].text)

    res[f't{team}p{number}_recent_adr'] = \
        float(driver.find_elements(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')[4].text)

    res[f't{team}p{number}_recent_kpr'] = \
        float(driver.find_elements(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')[5].text)

    return res


def make_url(player_url: str, match_date, weeks=None):
    '''создает ссылку из даты матча и колличества недель назад '''
    yesterday = date.fromisoformat(match_date) - timedelta(days=1)
    if weeks is None:
        starting_date = '2012-01-01'
    else:
        starting_date = yesterday - timedelta(weeks=weeks)
    split = player_url.split('/')
    url = 'https://www.hltv.org/stats/players/'+split[-2]+f"/{split[-1]}?startDate={starting_date}&endDate={yesterday}"
    return url


def extract_player_full_stats(driver: Chrome, team_number, number, suffix=''):
    ''' возвращает расширеную статистику игрока без продвинутой статистики'''
    res = {}
    if suffix != '':
        suffix += '_'
    for e in driver.find_elements(By.CSS_SELECTOR, '.stats-row'):
        spans = e.find_elements(By.CSS_SELECTOR, 'span')
        if '%' in spans[1].text:
            res[f't{team_number}p{number}_' + suffix + spans[0].text.lower()] = spans[1].text
            continue
        if spans[0].text == 'Rating 1.0' or spans[0].text == 'Rating 2.0':
            # res[f't{team_number}p{number}_' + suffix + 'rating'] = float(spans[1].text)
            continue
        res[f't{team_number}p{number}_' + suffix + spans[0].text.lower()] = float(spans[1].text)

    return res


def get_player_full_stats(driver: Chrome, player_url, match_date,
                          team_number, number, weeks, suffix):
    url = make_url(player_url, match_date, weeks)
    get(driver, url, 'player')
    return extract_player_full_stats(driver, team_number, number, suffix)


def get_player_stats(driver: Chrome, player_url, match_date, team_number, number):
        '''yesterday = date.fromisoformat(match_date) - timedelta(days=1)
        start_date = '2012-01-01'
        split = player_url.split('/')
        url = 'https://www.hltv.org/stats/players/'+split[-2]+f"/{split[-1]}?startDate={start_date}&endDate={yesterday}"'''
        url = make_url(player_url, match_date)

        res = {}

        '''while True:
            try:
                driver.get(url)
                driver.find_element(By.TAG_NAME,'body')
                driver.find_element(By.CSS_SELECTOR,'.summaryStatBreakdownDataValue')
            except TimeoutException:
                #traceback.print_exc()
                continue
            except NoSuchElementException:
                #traceback.print_exc()
                continue
            except Exception as e:
                #traceback.print_exc()
                print(str(e))
                if 'ERR_PROXY_CONNECTION_FAILED' in str(e) or 'ERR_CONNECTION_RESET' in str(e) :
                    #driver.quit()
                    #driver = make_driver(proxy)
                    continue
                driver.quit()
                raise e
            else:
                break '''
        get(driver, url, 'player')

        try:
            res[f't{team_number}p{number}_rating'] = float(driver.find_elements(By.CSS_SELECTOR,
                                                                                '.summaryStatBreakdownDataValue')[0].text)
            res[f't{team_number}p{number}_dpr'] = float(driver.find_elements(By.CSS_SELECTOR,
                                                                             '.summaryStatBreakdownDataValue')[1].text)
            res[f't{team_number}p{number}_kast'] = float(re.findall("\d+\.\d+", driver.find_elements(By.CSS_SELECTOR,
                                                                                                     '.summaryStatBreakdownDataValue')[2].text)[0])
            res[f't{team_number}p{number}_impact'] = float(driver.find_elements(By.CSS_SELECTOR,
                                                                                '.summaryStatBreakdownDataValue')[3].text)
            res[f't{team_number}p{number}_adr'] = float(driver.find_elements(By.CSS_SELECTOR,
                                                                             '.summaryStatBreakdownDataValue')[4].text)
            res[f't{team_number}p{number}_kpr'] = float(driver.find_elements(By.CSS_SELECTOR,
                                                                             '.summaryStatBreakdownDataValue')[5].text)
            res[f't{team_number}p{number}_country'] = driver.find_element(By.CSS_SELECTOR,
                                                                          'div.summaryRealname.text-ellipsis img.flag').get_attribute('title')
        except Exception as e:
            driver.quit()
            raise e

        #age
        try:
            res[f't{team_number}p{number}_age'] = int(re.findall(r'\d+', driver.find_element(By.CSS_SELECTOR,'div.summaryPlayerAge').text)[0])
        except IndexError:
            res[f't{team_number}p{number}_age'] = 0
        
        return res


def get_recent_stats(driver: Chrome,
                     player_url,
                     match_date,
                     weeks,
                     team_number,
                     number):
    '''yesterday = date.fromisoformat(match_date) - timedelta(days=1)
    start_date = yesterday - timedelta(weeks=weeks)
    split = player_url.split('/')
    url = 'https://www.hltv.org/stats/players/'+split[-2]+f"/{split[-1]}?startDate={start_date}&endDate={yesterday}"'''

    res = {}

    url = make_url(player_url, match_date, weeks)

    get(driver, url, 'player')

    try:
        res[f't{team_number}p{number}_recent_rating'] =\
              float(driver.find_elements(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')[0].text)

        res[f't{team_number}p{number}_recent_dpr'] =\
            float(driver.find_elements(By.CSS_SELECTOR, '.summaryStatBreakdownDataValue')[1].text)

        res[f't{team_number}p{number}_recent_kast'] = \
            float(re.findall("\d+\.\d+", driver.find_elements(By.CSS_SELECTOR,
                                                              '.summaryStatBreakdownDataValue')[2].text)[0])

        res[f't{team_number}p{number}_recent_impact'] = float(driver.find_elements(By.CSS_SELECTOR,
                                                                                   '.summaryStatBreakdownDataValue')[3].text)
        res[f't{team_number}p{number}_recent_adr'] = float(driver.find_elements(By.CSS_SELECTOR,
                                                                                '.summaryStatBreakdownDataValue')[4].text)
        res[f't{team_number}p{number}_recent_kpr'] = float(driver.find_elements(By.CSS_SELECTOR,
                                                                                '.summaryStatBreakdownDataValue')[5].text)
    except Exception as e:
        driver.quit()
        raise e

    return res


def get(driver: Chrome,
        url: str,
        page_type: Literal['match', 'player', 'team'] = 'match') -> None:
    while True:
        try:
            driver.get(url)
            driver.find_element(By.TAG_NAME, 'body')
            if page_type == 'match':
                driver.find_element(By.CSS_SELECTOR,
                                    '.team2-gradient')
            elif page_type == 'player':
                driver.find_element(By.CSS_SELECTOR,
                                    '.summaryStatBreakdownDataValue')
            elif page_type == 'team':
                driver.find_element(By.CSS_SELECTOR,
                                    'a.col-custom')
            else:
                raise ValueError
        except TimeoutException:
            continue
        except NoSuchElementException:
            continue
        except Exception as e:
            # traceback.print_exc()
            print(str(e))
            if ('ERR_PROXY_CONNECTION_FAILED' in str(e)
                    or 'ERR_CONNECTION_RESET' in str(e)):
                # driver.quit()
                # driver = make_driver(proxy)
                continue
            # net::ERR_CONNECTION_RESET
            driver.quit()
            raise e
        else:
            break


def process_team_page(driver: Chrome, team_n) -> dict:
    '''
    returns team name, team country, team rank from team page
    '''

    res = {}
    res[f't{team_n}_name'] = driver.find_element(By.CSS_SELECTOR,
                                                 '.profile-team-name.text-ellipsis').text
    res[f'team{team_n}_country'] = driver.find_element(By.CSS_SELECTOR,
                                                       '.team-country.text-ellipsis img').get_attribute('title')
    res[f'team{team_n}_rank'] = int(re.findall(r'\d+', driver.find_elements(By.CSS_SELECTOR,
                                                                            '.profile-team-stat a')[0].text)[0])
    return res


def get_player_urls(driver: Chrome) -> list[str]:
    '''
    returns player urls from team page
    '''
    return list(map(lambda x: x.get_attribute('href'),
                    driver.find_elements(By.CSS_SELECTOR,
                                         '.bodyshot-team.g-grid a')))


def process_fantasy_match(team0_url, team1_url, proxy=None):
    driver = make_driver(proxy,
                         30,
                         15)
    res = {}
    res['date'] = str(datetime.now().date())

    get(driver,
        team0_url,
        'team')
    team1_players = get_player_urls(driver)
    res.update(process_team_page(driver,
                                 1))

    get(driver,
        team1_url,
        'team')
    team2_players = get_player_urls(driver)
    res.update(process_team_page(driver,
                                 2))

    res['lan'] = 0

    def exctract_players_data(driver: Chrome,
                              urls: list[str],
                              date: str,
                              team_n: int):
        res = {}
        for number, player_url in enumerate(urls):
            res.update(get_player_stats(driver,
                                        player_url,
                                        date,
                                        team_n,
                                        number))
            res.update(get_recent_stats(driver,
                                        player_url,
                                        date,
                                        12,
                                        team_n,
                                        number))
        return res

    res.update(exctract_players_data(driver,
                                     team1_players,
                                     res['date'],
                                     1))
    res.update(exctract_players_data(driver,
                                     team2_players,
                                     res['date'],
                                     2))

    driver.quit()
    return res


def get_team_names(driver: Chrome) -> dict[str:str]:
    res = {}
    res['t1_name'] = driver.find_elements(By.CSS_SELECTOR, '.standard-box.teamsBox .team .teamName')[0].text
    res['t2_name'] = driver.find_elements(By.CSS_SELECTOR, '.standard-box.teamsBox .team .teamName')[1].text
    return res


def get_winstreaks(driver: Chrome) -> dict[str, str]:
    res = {}
    res['t1_winstreak'] = (
        int(driver.find_elements(By.CSS_SELECTOR, '.past-matches-box.text-ellipsis')[2]
            .text.splitlines()[1][:2])
        if 'streak' in driver.find_elements(By.CSS_SELECTOR, '.past-matches-box.text-ellipsis')[2].
        text.splitlines()[1]
        else 0)
    res['t2_winstreak'] = (
        int(driver.find_elements(By.CSS_SELECTOR, '.past-matches-box.text-ellipsis')[3]
            .text.splitlines()[1][:2])
        if 'streak' in driver.find_elements(By.CSS_SELECTOR, '.past-matches-box.text-ellipsis')[3].
        text.splitlines()[1]
        else 0)
    return res


def get_face_to_face_stats(driver: Chrome) -> dict[str, str]:
    res = {}
    res['t1_wins'] = driver.find_elements(By.CSS_SELECTOR,
                                          '.head-to-head .bold')[0].text
    res['draws'] = driver.find_elements(By.CSS_SELECTOR,
                                        '.head-to-head .bold')[1].text
    res['t2_wins'] = driver.find_elements(By.CSS_SELECTOR,
                                          '.head-to-head .bold')[2].text
    return res


def get_map_stats(driver: Chrome) -> dict:
    res = {}
    for e in driver.find_elements(By.CSS_SELECTOR,
                                  '.map-stats-infobox-maps'):
        map_name = e.find_element(By.CSS_SELECTOR,
                                  '.map-stats-infobox-mapname-container').text
        res[f't1_{map_name}'] = e.find_elements(By.CSS_SELECTOR,
                                                '.map-stats-infobox-stats .a-reset')[0].text
        res[f't2_{map_name}'] = e.find_elements(By.CSS_SELECTOR,
                                                '.map-stats-infobox-stats .a-reset')[1].text
    return res


def get_result(driver: Chrome) -> dict:
    res = {}
    res['team2_score'] = driver.find_element(By.CSS_SELECTOR,
                                             '.team2-gradient').find_element(By.CSS_SELECTOR,
                                                                             '.won,.lost').text
    res['team1_score'] = driver.find_element(By.CSS_SELECTOR,
                                             '.team1-gradient').find_element(By.CSS_SELECTOR,
                                                                             '.won,.lost').text
    return res


def get_countries(driver: Chrome) -> dict[str, str]:
    res = {}
    res['team1_country'] = driver.find_element(By.CSS_SELECTOR,
                                               'img.team1').get_attribute('title')
    res['team2_country'] = driver.find_element(By.CSS_SELECTOR,
                                               'img.team2').get_attribute('title')
    return res


def is_lan(driver: Chrome) -> bool:
    return 'LAN' in driver.find_element(By.CSS_SELECTOR,
                                        'div.padding.preformatted-text').text


def get_date(driver: Chrome) -> date:
    d = driver.find_element(By.CSS_SELECTOR,
                            'div.date').get_attribute('data-unix')
    return date.fromtimestamp(int(d)//1000)


def get_rank(driver: Chrome, team: int):
    return re.findall(r'\d+', driver.find_elements(By.CSS_SELECTOR,
                                                   'div.teamRanking a.a-reset')[team-1].text)[0]


def get_player_links(driver: Chrome, team: int) -> list[str]:
    '''
    returns player urls from match page
    '''
    if team == 1:
        return list(map(lambda obj: obj.get_attribute('href'),
                        driver.find_elements(By.CSS_SELECTOR,
                                             'td.player.player-image a'
                                             )))[:5]
    return list(map(lambda obj: obj.get_attribute('href'),
                    driver.find_elements(By.CSS_SELECTOR,
                                         'td.player.player-image a'
                                         )))[5:]


def process_match(url: str, proxy: str = None,
                  history: bool = False,
                  extended: bool = False
                  ) -> dict[str, any]:

    driver = make_driver(proxy, 30, 15)

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

            driver.get(team1_url)
            team1_players = list(map(lambda x: x.get_attribute('href'),
                                     driver.find_elements(By.CSS_SELECTOR,
                                                          '.bodyshot-team.g-grid a')))
            driver.get(team2_url)
            team2_players = list(map(lambda x: x.get_attribute('href'),
                                     driver.find_elements(By.CSS_SELECTOR,
                                                          '.bodyshot-team.g-grid a')))

            if not team1_players:
                raise ValueError('невозможно извлечь ссылки на профили игроков')

            if not team2_players:
                raise ValueError('невозможно извлечь ссылки на профили игроков')

    except Exception as e:
        driver.quit()
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

    return res


def wrapper(url: str, bad_urls: list, proxy: str = None) -> dict[str, any]:

    if url in bad_urls:
        return 'bad url'
    try:
        return process_match(url, proxy, history=True)
    except (IndexError, NoSuchElementException) as e:
        bad_urls.append(url)
        return e
    except Exception as e:
        return e


proxies = ['/home/sasha/Documents/vscode/hltv parsing/proxies/0',
           '/home/sasha/Documents/vscode/hltv parsing/proxies/1',
           '/home/sasha/Documents/vscode/hltv parsing/proxies/2',
           '/home/sasha/Documents/vscode/hltv parsing/proxies/3',
           None]


if __name__ == '__main__':
    # urls = open('top_links.txt').read().splitlines()
    urls = open('list.txt').read().splitlines()
    bad_urls = open('bad_urls_ext.txt').read().splitlines()
    data = pd.read_csv('hltv_ext.csv')
    # data = pd.read_csv('hltv2.csv')
    # data = pd.DataFrame()
    result = []

    urls = ['https://www.hltv.org'+url for url in urls]

    data = data.drop_duplicates()

    begining_time = datetime.now()

    manager = Manager()
    bad_urls = manager.list(bad_urls)

    pool = Pool(8)
    res = pool.starmap(
        wrapper,
        sample(
            [
                (url, bad_urls, choice(proxies))
                for url in list(set(urls)
                                .difference(list(data['url']))
                                .difference(bad_urls))
                             ],
            k=100
            )
        )

    result = []
    for e in res:
        if type(e) is dict:
            result.append(e)
            continue
        print(e)

    print('всего страниц собрано:', len(result))
    print('всего осталось:', len(list(set(urls)
                                      .difference(list(data['url']))
                                      .difference(bad_urls)))-len(result))

    pd.concat([data, pd.DataFrame(result)]).to_csv('hltv_ext.csv', index=False)

    with open('bad_urls_ext.txt', 'w') as file:
        file.write('\n'.join(bad_urls))

    print('begining time:', begining_time)
    print('ending time:', datetime.now())
    print('time consumed:', datetime.now() - begining_time)

    # Message: unknown error: cannot determine loading status
