# douyin_downloader
抖音文件批量下载工具

一、功能

1、2022.09.30 

批量下载特定用户、或者用户列表的视频文件和图片的基本功能

DouyinDownloader类中也有下载特定视频的函数，有需要的可自行调用。


二、使用方法

1、从抖音用户主页点击分享后，选择复制链接

2、将链接写到程序文件夹的user_url_list.txt，每个用户一行

3、运行程序，特定用户的文件将放置到download对应的用户目录下


三、注意事项

1、程序为使用python3编写，需自行安装所需依赖包selenium、bs4、re、json、requests等

2、需要安装chrome浏览器，并将对应版本的chromedriver放到当前目录

3、程序兼容windows和Ubuntu


三、存在问题（2022.09.30）

1、对图片格式的下载，打开页面返回的response有多种，有时存在不能下载的情况，重新运行有时可解决

2、读取的用户名称，有时前面会有空格，有时没有，使得同一个用户可能创建两个目录

3、多个用户网址放入user_url_list.txt时，只能读取1个数据，第二个就报错

4、视频名称为视频IP加视频文字内容，个别情况下视频文件获取失败时，此时获得文件名缺乏文字内容

