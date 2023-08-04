# Batch download tools for Douyin videos and pictures
# @author  palm.wang@hotmail.com
# version 1.0, 2022.09.28 : basic user video and picture download function
# version 1.1, 2022.10.03 : 1) data download update, 2) try more than once to fetch notes
# version 1.1.1, 2023.04.05 : add some delay at start time, u should handcheck the douyin page, then to continue
# version 1.1.2, 2023.07.29 : add the "execute_script" process after page has been loaded, to acquire the real web content, and to get the web address of video and picture.

import random
import time
import re
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import os
import numpy as np
import json

import threading
import subprocess

# def start_chrome_exiplicit():
#     cmd = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe --remote-debugging-port=9223 --user-data-dir='selenium_ChromeProfile'"
#     subprocess.run(cmd)


# General web browser using selenium and chrome
class WebBrowser:
    def __init__(self, driver_path, silent=False):
        # chrome_thread = threading.Thread(target=start_chrome_exiplicit)
        # chrome_thread.start()
        self.chrome_options = webdriver.ChromeOptions()
        # self.chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9223")

        self.driver_path = driver_path
        if silent:   # set Chrome to run under background
            self.chrome_options.add_argument('--headless')
            self.chrome_options.add_argument('--disable-gpu')
        # Open Chrome browser
        self.browser = webdriver.Chrome(executable_path=self.driver_path, options=self.chrome_options)

        # # added js code to avoid crawler detection @pw 20230405
        # with open('./stealth.min.js') as f:
        #     print('open js file OK')
        #     js = f.read()
        # self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js})

    # Close browser Tab
    def close_browser_tab(self):
        self.browser.close()

    # Quit browser, close the full window
    def close_entire_browser(self):
        self.browser.quit()

    # Quit and reopen the browser
    def reopen_browser(self):
        self.browser.quit()
        # Open Chrome browser
        self.browser = webdriver.Chrome(executable_path=self.driver_path, options=self.chrome_options)

    # Get page source of the specific url using browser
    # Attention: the dynamic webpage cannot be acquired with requests.get(url)
    def get_main_page_source(self, url, first_time_download=False):
        try:
            self.browser.get(url)
            if first_time_download:
                time.sleep(30)
                # self.browser.get(url)
            return self.browser.page_source
        except Exception as e:
            print('Unable to open url: %s', url)
            print(e)

    # Load and get the full page with scrolling
    def get_full_page_source(self):
        self.scroll_the_page_to_the_end()
        return self.browser.page_source

    # Close the nonsense little account window
    # Find the position of the 'x' class, and take a click function
    def close_nonsense_window_by_class(self, item_class):
        try:
            self.browser.find_element("class name", item_class).click()
            # self.browser.find_element(By.CLASS_NAME, item_class).click()
        # except Exception as e:
        except:
            print('There is no class name: %s', item_class)
            # print(e)

    # scroll the page to the end, to load the full page
    def scroll_the_page_to_the_end(self):
        # Scroll to the end of the page, in order to load the full page
        # Reference: https://blog.csdn.net/cai5/article/details/114250924
        get_height_js = 'return action=document.body.scrollHeight'
        scroll_height_js = 'window.scrollTo(0, document.body.scrollHeight)'
        height = self.browser.execute_script(get_height_js)
        self.browser.execute_script(scroll_height_js)
        time.sleep(5)
        t1 = int(time.time())
        status = True
        num = 0
        cnt = 0
        equal_num = 0
        while status and cnt < 100:
            t2 = int(time.time())
            if t2 - t1 < 30:
                cnt = cnt + 1
                n_height = self.browser.execute_script(get_height_js)
                if n_height > height:
                    self.browser.execute_script(scroll_height_js)
                    time.sleep(1)
                    height = n_height
                    t1 = int(time.time())
                elif n_height == height:
                    equal_num = equal_num + 1
                    if equal_num >= 5:
                        break
            elif num < 3:
                time.sleep(3)
                num = num + 1
            else:
                status = False
                break


# Douyin video and picture downloader
class DouyinDownloader:
    def __init__(self, driver_path, data_path, browser_silent=False):
        self.web_browser = WebBrowser(driver_path, browser_silent)
        self.data_path = data_path
        self.max_try_cnt = 5
        self.last_index_file = 'start_user_index.json'

    # Find the video id from the input string
    def get_video_list_from_string(self, str_data):
        video_strs_pattern1 = r'<a href="/video/(.*?)"'
        video_list = re.findall(video_strs_pattern1, str_data)
        print('video_list1: ', video_list)
        if len(video_list) == 0:
            video_strs_pattern2 = r'<a href="//www.douyin.com/video/(.*?)"'
            video_list = re.findall(video_strs_pattern2, str_data)
            print('video_list2: ', video_list)
        return video_list

    # Find the note(picture) id from the input string
    def get_note_list_from_string(self, str_data):
        note_strs_pattern1 = r'<a href="/note/(.*?)"'
        note_list = re.findall(note_strs_pattern1, str_data)
        print('note_list1: ', note_list)
        if len(note_list) == 0:
            note_strs_pattern2 = r'<a href="//www.douyin.com/note/(.*?)"'
            note_list = re.findall(note_strs_pattern2, str_data)
            print('note_list2: ', note_list)
        return note_list

    # Get the real video url from video page
    def get_real_video_url_from_videopage(self, video_id, user_data_path):
        video_url = "https://www.douyin.com/video/{0}".format(video_id)
        page_source1 = self.web_browser.get_main_page_source(video_url)

        # added @pw 20230729
        time.sleep(2)
        page_source2 = self.web_browser.browser.execute_script("return document.documentElement.innerHTML;")

        soup_data = str(BeautifulSoup(page_source2, 'html.parser'))
        real_video_url_pattern = r'www.douyin.com/aweme/v1/play/(.*?)"'
        real_video_url_str = re.findall(real_video_url_pattern, soup_data)

        # print(soup_data)  #For test 20230710
        if len(real_video_url_str) == 0:
            # This is a note page
            # print(soup_data)
            print('parse notes in video page...')
            # user_data_path = './{0}/{1}'.format(self.data_path, user_id)
            num_note = self.download_note_in_video_page(soup_data, user_data_path, video_id)
            if num_note > 0:
                ret_str = 'NoteInVideoPage'
            else:
                ret_str = ''
            return '', ret_str
        real_video_url = 'https://www.douyin.com/aweme/v1/play/' + real_video_url_str[0]
        # find the video title
        video_title_pattern = r'<title>(.*?) - æŠ–éŸ³</title>'
        video_title_str = re.findall(video_title_pattern, soup_data)
        if len(video_title_str) == 0:
            print("title not found")
            # print("title not found: ", soup_data)
            return real_video_url, ''
            # print('real_video_url: %s', real_video_url)
        # print('video title: %s', video_title_str)
        return real_video_url, video_title_str[0]

    def download_note_in_video_page(self, soup_data, user_data_path, video_id):
        real_note_url_pattern = r'<img class="V5BLJkWV" src="(.*?)"'
        real_note_url_strs = re.findall(real_note_url_pattern, soup_data)
        real_note_urls = []
        print(real_note_url_strs)
        for i in range(len(real_note_url_strs)):
            temp_url = str(real_note_url_strs[i]).replace('&amp;', '&')
            real_note_urls.append(temp_url)
        print('real_note_urls in video page: ', real_note_urls)
        for j in range(len(real_note_urls)):
            file_name = "{0}/{1}_{2}.webp".format(user_data_path, video_id, j)
            self.download_image(real_note_urls[j], file_name)
            time.sleep(random.random() * 1)
        return len(real_note_urls)

    # Get the real notes url from note page
    def get_real_note_urls_from_notepage(self, note_id):
        note_url = "https://www.douyin.com/video/{0}".format(note_id)
        page_source1 = self.web_browser.get_main_page_source(note_url)

        # added @pw 20230729
        time.sleep(2)
        page_source2 = self.web_browser.browser.execute_script("return document.documentElement.innerHTML;")
        # self.web_browser.close_nonsense_window_by_class('dy-account-close')
        soup_data = str(BeautifulSoup(page_source2, 'html.parser'))
        # print(soup_data)
        real_note_url_pattern = r'<img class="V5BLJkWV" src="(.*?)"'
        real_note_url_strs = re.findall(real_note_url_pattern, soup_data)
        real_note_urls = []
        print(real_note_url_strs)
        for i in range(len(real_note_url_strs)):
            temp_url = str(real_note_url_strs[i]).replace('&amp;', '&')
            real_note_urls.append(temp_url)
        print('real_note_urls: ', real_note_urls)
        # if len(real_note_urls) == 0:
        #     print(soup_data)
        #     exit(0)
        return real_note_urls

    # download one video stream
    def download_video_stream(self, video_url, video_file_name):
        try:
            if os.path.isfile(video_file_name):
                # # Ignore the file if the file exist
                print("%s was downloaded ok\n" % video_file_name)
                return True
                # # re-download the file if the file exist
                # os.remove(video_file_name)

            video_response = requests.get(video_url, stream=True)
            with open(video_file_name, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print("%s is downloaded ok\n" % video_file_name)
            f.close()
            return True
        except Exception as e:
            print("failed to download video (url=", video_url, ")")
            print(e)
            return False

    # Download the specified video_list
    def download_specified_videos(self, video_list, user_data_path):
        # Download the videos
        video_num = len(video_list)
        # video_num = 1  # For test ...
        for i in range(video_num):
            video_url = []
            for try_i in range(self.max_try_cnt):  # Try to get the url (it maybe fail, try max_try_cnt)
                print('try_i: ', try_i)
                video_url, video_title = self.get_real_video_url_from_videopage(video_list[i], user_data_path)
                if len(video_url) > 0:  #
                    break
                elif video_title == 'NoteInVideoPage':
                    print('download note in video page')
                    break
                else:
                    time.sleep(random.random() * 8)
            if video_url == '':
                print('video url not found or note in video url!')
                continue
            # file_name = "{0}/{1}.mp4".format(user_data_path, video_list[i])
            video_title1 = re.sub(r"[\/\\\:\*\?\"\<\>\|]", "", video_title)
            file_name = "{0}/{1}.mp4".format(user_data_path, '{0}_{1}'.format(video_list[i], video_title1))
            self.download_video_stream(video_url, file_name)
            time.sleep(random.random()*3)

    # Download one webp image
    def download_image(self, image_url, iamge_file_name):
        if os.path.isfile(iamge_file_name):
            # # Ignore the file if the file exist
            print("%s was downloaded ok\n" % iamge_file_name)
            return True
        response = requests.get(url=image_url, stream=True)
        with open(iamge_file_name, 'wb') as f:
            f.write(response.content)

    # Download the specified note_list
    def download_specified_notes(self, note_list, user_data_path):
        # Download the notes
        note_num = len(note_list)
        for i in range(note_num):
            note_urls = []
            for try_i in range(self.max_try_cnt):  # Try to get the url (it maybe fail, try max_try_cnt)
                print('try_i: ', try_i)
                note_urls = self.get_real_note_urls_from_notepage(note_list[i])
                if len(note_urls) > 0:  #
                    break
                else:
                    time.sleep(random.random() * 2)
            for j in range(len(note_urls)):
                file_name = "{0}/{1}_{2}.webp".format(user_data_path, note_list[i], j)
                self.download_image(note_urls[j], file_name)
                time.sleep(random.random() * 1)

    # Get user url from 4 kinds of input string
    # take the main page of 'Missingziyu' for example, u can input:
    #  str01 = '6GAWU8G'
    #  str02 = 'https://v.douyin.com/6GAWU8G/'
    #  str03 = 'MS4wLjABAAAAeeO77c3knyeN7D2RD6f9YbcGXl2-RRvcHluTiLwWmt8LsRaaeICfEdkwgdwYwpP_'
    #  str04 = 'https://www.douyin.com/user/MS4wLjABAAAAeeO77c3knyeN7D2RD6f9YbcGXl2-RRvcHluTiLwWmt8LsRaaeICfEdkwgdwYwpP_'
    def get_user_url_and_user_id(self, input_str):
        user_url_pattern01 = r'https://v.douyin.com/(.*?)/'
        user_url_pattern02 = r'https://www.douyin.com/user/(.*)'
        user_id01 = re.findall(user_url_pattern01, input_str)
        user_id02 = re.findall(user_url_pattern02, input_str)

        # Type1: https://v.douyin.com/6GAWU8G/
        if len(user_id01) > 0:
            user_id = user_id01[0]
            user_url = 'https://v.douyin.com/{0}/'.format(user_id)
        # Type2: https://www.douyin.com/user/MS4wLjABAAAAeeO77c3knyeN7D2RD6f9YbcGXl2-RRvcHluTiLwWmt8LsRaaeICfEdkwgdwYwpP_
        elif len(user_id02) > 0:
            user_id = user_id02[0]
            user_url = 'https://www.douyin.com/user/{0}'.format(user_id)
        else:
            if len(input_str) < 10:
                user_id = input_str
                user_url = 'https://v.douyin.com/{0}/'.format(user_id)
            else:
                user_id = input_str
                user_url = 'https://www.douyin.com/user/{0}'.format(user_id)
        print(user_id, user_url)
        return user_url, user_id

    # get user_name from the input string
    def get_user_name_from_string(self, str_data):
        # print(str_data)
        # str_data = '<span class="kbjj_psh">æŠ–éŸ³å·ï¼š Missingziyu</span><span class="WXnH80ht">IPå±žåœ°ï¼šæµ™æ±Ÿ</span></p>'
        user_name_pattern = r'æŠ–éŸ³å·ï¼š(.*?)</span>'
        user_name = re.findall(user_name_pattern, str_data)
        if len(user_name) == 0:
            print(str_data)
            true_user_name = 'NameNotFound'
            raise Exception("User Name not found, maybe u are downloading files too frequently!")
        else:
            # print('user_name: ', user_name[0])
            true_user_name0 = user_name[0].strip()
            true_user_name1 = re.sub(r"<!-- -->", "", true_user_name0)
            true_user_name = re.sub(r"[\/\\\:\*\?\"\<\>\|\.]", "", true_user_name1)
        return true_user_name

    def get_user_data_list(self, user_url, first_time_download):
        # Open the user url web page
        self.web_browser.get_main_page_source(user_url, first_time_download)
        # Click on the 'x' of the account dy-account window
        time.sleep(2)
        self.web_browser.close_nonsense_window_by_class('dy-account-close')
        # roll the page to the end to loading the full page
        page_source = self.web_browser.get_full_page_source()
        user_name = self.get_user_name_from_string(page_source)
        video_list = self.get_video_list_from_string(page_source)
        note_list = self.get_note_list_from_string(page_source)
        return video_list, note_list, user_name

    def filter_out_exist_list(self, in_video_list, in_note_list, user_id):
        # user_data_path = './{0}/{1}'.format(self.data_path, user_id)
        user_data_path, ret_user_id = self.set_download_file_path(user_id)
        print(user_data_path)
        if not os.path.exists(user_data_path):  # have not downloaded this user data yet
            out_video_list = in_video_list
            out_note_list = in_note_list
            os.makedirs(user_data_path)
        else:
            dir_files = os.listdir(user_data_path)
            downloaded_list = []
            for dir_file in dir_files:
                tmp_data = dir_file.split('_')
                downloaded_list.append(tmp_data[0])
            not_downloaded_video_list = list(set(in_video_list)-set(downloaded_list))
            not_downloaded_note_list = list(set(in_note_list) - set(downloaded_list))
            out_video_list = not_downloaded_video_list
            out_note_list = not_downloaded_note_list
            # print('in_video_list: ', in_video_list)
            # print('in_note_list: ', in_note_list)
            # print('downloaded_list: ', downloaded_list)
            print('not_downloaded_video_list[{0}]:{1}'.format(len(not_downloaded_video_list), not_downloaded_video_list))
            print('not_downloaded_note_list[{0}]:{1}'.format(len(not_downloaded_note_list), not_downloaded_note_list))
        return out_video_list, out_note_list, user_data_path, ret_user_id

    def set_download_file_path(self, user_id):
        ret_user_id = user_id
        # if no user_id is set, set it to be 'general'
        if user_id == '':
            user_id = 'general'
        # check if the path exist, and mkdir if not exist
        tmp_user_data_path = './{0}/{1}'.format(self.data_path, user_id)
        tmp_data = user_id.split('_')
        tmp_num = len(tmp_data)
        if tmp_num >= 2:
            douyin_id = tmp_data[1]
            for mm in range(2, tmp_num-1):
                douyin_id = douyin_id+tmp_data[mm]
            # douyin_id = tmp_data[tmp_num-1]
            id_folder_list = []
            for file_folder in os.listdir('./{0}'.format(self.data_path)):
                if file_folder.endswith('_{0}'.format(douyin_id)):
                    id_folder_list.append(file_folder)
            print(id_folder_list)
            if len(id_folder_list) > 0:
                ret_user_id = id_folder_list[0]
                user_data_path = './{0}/{1}'.format(self.data_path, id_folder_list[0])
                print('user already exists: ', user_id, id_folder_list)
            else:
                user_data_path = tmp_user_data_path
                print('new user: ', user_id)
        else:
            user_data_path = tmp_user_data_path
            print('wrong user_id format: ', user_id)
        # print(user_data_path)
        return user_data_path, ret_user_id


    # Download specific user data (both video and notes)
    def download_specified_user_data(self, input_str, first_time_download):
        user_url, user_id = self.get_user_url_and_user_id(input_str)
        video_list, note_list, user_name = self.get_user_data_list(user_url, first_time_download)
        user_id = str(user_id).replace('_', '-')
        user_id = '{0}_{1}'.format(user_id, user_name)
        video_list, note_list, user_data_path, user_id = self.filter_out_exist_list(video_list, note_list, user_id)
        self.download_specified_videos(video_list, user_data_path)
        self.download_specified_notes(note_list, user_data_path)

    # load last downloading user index from the stored start_user_index.json
    def load_last_downloading_user_index(self, user_num):
        try:
            with open(self.last_index_file, "r") as fh:
                data = json.load(fh)
                start_index = int(data['start_user_index'])
                total_len = int(data['total_user_number'])
                # the user number in user_url_list.txt has changed, reset the start index to 0
                if total_len != '' and total_len != user_num:
                    start_index = 0
        except Exception as e:
            print(e)
            start_index = 0
            total_len = 0
        return start_index

    # save last downloading user index to the stored start_user_index.json
    def save_last_downloading_user_index(self, user_index, user_num):
        dict_v = {
            "start_user_index": str(user_index),
            "total_user_number": str(user_num)
        }
        try:
            with open(self.last_index_file, "w") as fh:
                json.dump(dict_v, fh, indent=4)
        except Exception as e:
            print(e)

    # Download a group of users, in list format
    def download_user_data(self, input_str_list, max_try_times):
        user_num = len(input_str_list)
        exception_user_i = self.load_last_downloading_user_index(user_num)
        first_time_download = True
        print('start user index: ', exception_user_i)
        # Try max_try_times Exceptions
        for try_i in range(max_try_times):
            print("\n\n\n************* Try times: ", try_i, "******************\n")
            try:
                user_i_start = exception_user_i
                for user_i in range(user_i_start, user_num):
                    exception_user_i = user_i
                    self.save_last_downloading_user_index(user_i, user_num)
                    print("download user_i = %d/%d", user_i, user_num)
                    self.download_specified_user_data(input_str_list[user_i], first_time_download)
                    if first_time_download:
                        first_time_download = False
                    time.sleep(random.random() * 5)
                break
            except Exception as e:
                self.web_browser.reopen_browser()
                time.sleep(60+random.random()*30)
                print(e)
                exception_user_i = exception_user_i + 1

