from douyin_download import DouyinDownloader
import re
import json


class ProgramConfiguration:
    def __init__(self):
        try:
            with open("config.json", "r") as config_fh:
                data = json.load(config_fh)
                self.data_path = data['data_path']
                self.driver_path = data['driver_path']
                self.browser_silent = data['browser_silent']
        except Exception as e:
            self.data_path = 'download'
            self.driver_path = './chromedriver'  # path of 'chromedriver'
            self.browser_silent = False  # Set to True, if you want to run chrome under background
            print(e)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # loading configuration
    prog_config = ProgramConfiguration()
    # Create douyin downloader instance
    douyin_downloader = DouyinDownloader(prog_config.driver_path, prog_config.data_path, prog_config.browser_silent)

    # # input the user url
    # user_url = input('Please Enter the copied user URL')

    # # Download the specific user data by two kinds of user_id and usr_url, including videos and notes(pictures)
    # user_id01 = '6GAWU8G'
    # user_url01 = 'https://v.douyin.com/6GAWU8G/'
    # user_id02 = 'MS4wLjABAAAAeeO77c3knyeN7D2RD6f9YbcGXl2-RRvcHluTiLwWmt8LsRaaeICfEdkwgdwYwpP_'
    # user_url02 = 'https://www.douyin.com/user/MS4wLjABAAAAeeO77c3knyeN7D2RD6f9YbcGXl2-RRvcHluTiLwWmt8LsRaaeICfEdkwgdwYwpP_'
    # douyin_downloader.download_specified_user_data(user_id01)

    with open("user_url_list.txt", "r") as fh:
        user_url_data = fh.read()
        user_urls = user_url_data.split("\n")
    if len(user_urls):
        print(user_urls)
        douyin_downloader.download_user_data(user_urls)



