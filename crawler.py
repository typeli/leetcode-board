import json
from lxml import html
import requests
from utils import get_today_unixtime, get_today_datetime, get_now_datatime
from utils import get_today_eight_oclock_datetime, get_today_eight_oclock_unixtime
from pymongo import MongoClient
import time


def get_user_submissions_us(username: str) -> int:
    homepage_url = "https://leetcode.com/{}"
    r = requests.get(homepage_url.format(username))
    root = html.fromstring(r.content)
    try:
        sub = root.xpath('//*[@id="base_content"]/div/div/div[1]/div[3]/ul/li[2]/span')[0].text.strip()
        return int(sub.replace(' ', '').split("/")[1])
    except IndexError as e:
        pass
    return 0


def get_user_submissions_cn(username: str) -> int:
    url = "https://leetcode-cn.com/graphql"
    session = requests.Session()
    profile_query = """
    query userPublicProfile($userSlug: String!) {
      userProfilePublicProfile(userSlug: $userSlug) {
        username
        submissionProgress {
          totalSubmissions
          waSubmissions
          acSubmissions
          reSubmissions
          otherSubmissions
          acTotal
          questionTotal
          __typename
        }
        __typename
      }
    }
    """
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                 "Chrome/44.0.2403.157 Safari/537.36 "

    params = {"operationName": "userPublicProfile", "variables": {"userSlug": username}, "query": profile_query}
    json_data = json.dumps(params).encode("utf8")
    headers = {"User-Agent": user_agent,
               "Connection": "keep-alive",
               "Content-Type": "application/json",
               "Referer": f"https://leetcode-cn.com/u/{username}"}
    r = session.post(url, data=json_data, headers=headers)
    j = json.loads(r.content.decode())
    return j["data"]["userProfilePublicProfile"]["submissionProgress"]["totalSubmissions"]


def get_user_submissions(username: str, location: str) -> int:
    if location == "us":
        return get_user_submissions_us(username)
    elif location == "cn":
        return get_user_submissions_cn(username)


def get_user_total_solved_us(username: str) -> int:
    homepage_url = "https://leetcode.com/{}"
    r = requests.get(homepage_url.format(username))
    root = html.fromstring(r.content)
    try:
        solved = root.xpath('//*[@id="base_content"]/div/div/div[1]/div[3]/ul/li[1]/span')[0].text.strip()
        return int(solved.replace(' ', '').split("/")[0])
    except IndexError as e:
        pass
    return 0


def get_user_total_solved_cn(username: str) -> int:
    url = "https://leetcode-cn.com/graphql"
    session = requests.Session()
    profile_query = """
    query userPublicProfile($userSlug: String!) {
      userProfilePublicProfile(userSlug: $userSlug) {
        username
        submissionProgress {
          totalSubmissions
          waSubmissions
          acSubmissions
          reSubmissions
          otherSubmissions
          acTotal
          questionTotal
          __typename
        }
        __typename
      }
    }
    """
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                 "Chrome/44.0.2403.157 Safari/537.36 "

    params = {"operationName": "userPublicProfile", "variables": {"userSlug": username}, "query": profile_query}
    json_data = json.dumps(params).encode("utf8")
    headers = {"User-Agent": user_agent,
               "Connection": "keep-alive",
               "Content-Type": "application/json",
               "Referer": f"https://leetcode-cn.com/u/{username}"}
    r = session.post(url, data=json_data, headers=headers)
    j = json.loads(r.content.decode())
    return j["data"]["userProfilePublicProfile"]["submissionProgress"]["acTotal"]


def get_user_solved(username: str, location: str) -> int:
    if location == "us":
        return get_user_total_solved_us(username)
    elif location == "cn":
        return get_user_total_solved_cn(username)


def main():
    client = MongoClient()
    User = client["lcboard"]["User"]
    Record = client["lcboard"]["Record"]
    users = User.find({})
    for user in users:
        submissions = get_user_submissions(user["username"], user["location"])
        solved = get_user_solved(user["username"], user["location"])
        r = {"username": user["username"], "submission": submissions, "solved": solved,
                       "date": get_now_datatime(timezone=8)}
        print(r)
        Record.insert(r)
        time.sleep(1)


if __name__ == "__main__":
    main()
