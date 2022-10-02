# douyin_downloader
抖音文件批量下载工具

一、更新历史

1、2022.09.30 

批量下载特定用户、或者用户列表的视频文件和图片的基本功能

DouyinDownloader类中也有下载特定视频的函数，有需要的可自行调用。

2、2022.10.02

实现视频和图片的更新下载功能：对用户会先判断视频和图片清单是否已下载，只访问和获取未获取的内荣。因此，重新调用程序对相同用户的地址进行数据获取，就可以实现新视频和新图片的下载。


二、使用方法

1、从抖音用户主页点击分享后，选择复制链接

2、将链接写到程序文件夹的user_url_list.txt，每个用户一行

3、运行程序，特定用户的文件将下载到download对应的用户目录下


三、注意事项

1、程序为使用python3编写（测试版本3.8），需自行安装所需依赖包selenium、bs4、re、json、requests等

2、需要安装chrome浏览器，并将对应版本的chromedriver放到当前目录

3、程序兼容windows和Ubuntu

4、下载过程中会自动打开chrome浏览器，并自动打开需下载的页面，便于直观观察下载进度。代码中也编写了可以通过配置文件的隐藏浏览器的功能，但尚未测试是否会有问题。


四、存在问题

1、对图片格式的下载，打开页面返回的response有多种，有时存在不能下载的情况，重新运行有时可解决

2、视频名称为视频IP加视频文字内容，个别情况下视频文件的文字描述存在获取失败的情况，此时获得的文件名缺乏文字内容

3、下载一定数量网页后，会触发验证机制。目前尚未实现自动验证功能，需要手动验证。


五、后续完善工作

1、解决部分情况下图片或视频不能下载的问题，实现稳定下载
