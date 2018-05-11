import requests
import names
import time
import os
import sys
import Queue
import json
from threading import Thread, Lock
from random import randint, choice


def readconfig(filename):
    with open(filename, 'r') as config_json:
        config_data = config_json.read()
    return json.loads(config_data)


def verifydata(config):
    for data in config:
        if config[data] == "":
            print("{} is not filled out in config.json! Exiting...".format(data))
            sys.exit()


def readproxyfile(proxyfile):
    with open(proxyfile, "a+") as raw_proxies:
        proxies = raw_proxies.read().split("\n")
        proxies_list = []
        for individual_proxies in proxies:
            if individual_proxies.strip() != "":
                p_splitted = individual_proxies.split(":")
                if len(p_splitted) == 2:
                    proxies_list.append("http://" + individual_proxies)
                if len(p_splitted) == 4:
                    # ip0:port1:user2:pass3
                    # -> username:password@ip:port
                    p_formatted = "http://{}:{}@{}:{}".format(p_splitted[2], p_splitted[3], p_splitted[0], p_splitted[1])
                    proxies_list.append(p_formatted)
        proxies_list.append(None)
    return proxies_list


def unlock_p(rand_proxy):
    global p_list_lock, p_lock
    if (rand_proxy in p_list_lock) and (rand_proxy != None):
        with p_lock:
            p_list_lock.remove(rand_proxy)
            print("Released proxy: " + str(rand_proxy))


def genemail(rawemail):
    if rawemail[0] != "@":
        splitstuff = rawemail.split("@")
        for item in splitstuff:
            if item.strip() == "":
                splitstuff.remove(item)
        front = splitstuff[0]
        provider = splitstuff[1]
        bignum = str(randint(1, 1000000))
        return front + "+" + bignum + '@' + provider
    else:
        front = names.get_first_name() + names.get_last_name()
        splitstuff = rawemail.split("@")
        for item in splitstuff:
            if item.strip() == "":
                splitstuff.remove(item)
        provider = splitstuff[0]
        bignum = str(randint(1, 1000000))
        return front + bignum + "@" + provider


def request_recaptcha(service_key, google_site_key, pageurl):
    url = "http://2captcha.com/in.php?key=" + service_key + "&method=userrecaptcha&googlekey=" + google_site_key + "&pageurl=" + pageurl
    resp = requests.get(url)
    if resp.text[0:2] != 'OK':
        print("Error: {} Exiting...".format(resp.text))
        raise
    captcha_id = resp.text[3:]
    print("Successfully requested for captcha.")
    return captcha_id


def receive_token(captcha_id, service_key):
    global queue_, lock_
    fetch_url = "http://2captcha.com/res.php?key=" + service_key + "&action=get&id=" + captcha_id
    for count in range(1, 26):
        print("Attempting to fetch token. {}/25".format(count))
        resp = requests.get(fetch_url)
        if resp.text[0:2] == 'OK':
            grt = resp.text.split('|')[1]  # g-recaptcha-token
            print("Captcha token received.")
            return grt
        time.sleep(5)
    print("No tokens received. Restarting...")
    with lock_:
        queue_.put(1)
    raise


def enter_raffle():
    global queue_, q_lock, site_key, captcha_api, raffle_url, full_name, phone_num, raw_proxies
    while queue_.qsize() > 0:
        with q_lock:
            queue_.get()
        rand_proxy = choice(p_list)
        if not rand_proxy in p_list_lock:
            if rand_proxy != None:
                with p_lock:
                    p_list_lock.append(rand_proxy)
                    print("Using proxy: " + str(rand_proxy))
            with requests.session() as s:
                s.headers.update({
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "accept-encoding": "gzip, deflate, br",
                    "accept-language": "en-US,en;q=0.9",
                    "upgrade-insecure-requests": "1",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
                })
                a = s.get(raffle_url)
                print("Requesting raffle: " + str(raffle_url))
                a.raise_for_status()
                x = request_recaptcha(captcha_api, site_key, raffle_url)
                grt = receive_token(x, captcha_api)
                gen_email = genemail(raw_email)
                phonenum = config["phonenum"]
                zipcode = config["zipcode"]
                rand_sz = choice(range(4, 13))
                payload = {
                    "form": "3060071",
                    "viewkey": "Tlfx7CgsF3",
                    "unique_key": "77ddf69db1daf20622b5ad0d06977b66",
                    "password": "",
                    "hidden_fields": "",
                    "fspublicsession": "4d18b6bd6cc96b5e55e387742d7ae187",
                    "incomplete": "",
                    "incomplete_password": "",
                    "referrer": raffle_url,
                    "referrer_type": "js",
                    "_submit": "1",
                    "style_version": "3",
                    "viewparam": "766219",
                    "field64245509": full_name,
                    "field64245510": gen_email,
                    "field64245511": phonenum,
                    "field64245512": zipcode,
                    "field64245513": rand_sz,
                    "g-recaptcha-response": grt
                }
                ab = s.post("https://doverstreetmarketinternational.formstack.com/forms/index.php", data=payload, proxies={"https": rand_proxy}, timeout=30)
                print("Submitting raffle...")
                if ab.status_code == 200:
                    print("Successfully entered raffle.")
                    with w_lock:
                        with open("Entered.txt", "a+") as file:
                            file.write("{}:Size {}:{}:{}:{}\n".format(gen_email, rand_sz, full_name, phonenum, zipcode))
                else:
                    print("Failed to enter raffle.")
                    with q_lock:
                        queue_.put(1)
                unlock_p(rand_proxy)


def wrapper(num_enter):
    global queue_, q_lock
    for _ in range(num_enter):
        with q_lock:
            queue_.put(1)
    t_list = []
    for _ in range(10):
        t_list.append(Thread(target=enter_raffle))
    for t_ in t_list:
        t_.start()
    for t_ in t_list:
        t_.join()


if __name__ == "__main__":
    config = readconfig('config.json')
    verifydata(config)
    queue_ = Queue.Queue()
    q_lock = Lock()
    w_lock = Lock()
    p_list = readproxyfile(config["proxyfile"])
    p_lock = Lock()
    p_list_lock = []
    full_name = config["fullname"]
    raw_email = config["email"]
    raffle_url = config["url"]
    num_enter = config["how-many-times-do-you-want-to-enter-the-raffle"]
    captcha_api = config["2captcha-api"]
    site_key = config["raffle-sitekey"]
    wrapper(num_enter)
