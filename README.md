# douyin_downloader
抖音文件批量下载工具

一、更新历史

1、2022.09.30 

批量下载特定用户、或者用户列表的视频文件和图片的基本功能

DouyinDownloader类中也有下载特定视频的函数，有需要的可自行调用。

2、2022.10.02

实现视频和图片的更新下载功能：对用户会先判断视频和图片清单是否已下载，只访问和获取未获取的内荣。因此，重新调用程序对相同用户的地址进行数据获取，就可以实现新视频和新图片的下载。

3、2022.10.06

根据'抖音ID'判断用户是否已经存在，解决每个用户多次分享的 https://v.douyin.com/(user_id) ，user_id不一致，导致的同一个用户多次多个文件夹下载的问题。

4.2022.10.07

增加失败后，自动sleep 90秒左右重新接续下载的功能，尽量保证能够自动下载完全部作业。

5.2022.10.18

增加接续下载功能：在下载大量user的数据后，还是会出现验证码一直无法验证的问题。增加记录最后一次下载用户index的功能，可以手动停止后，继续从上一次下载到的用户开始接续下载。

6.2022.10.30

更正了一个使用“https://www.douyin.com/user/MS4wLjABAAAAeeO77c3knyeN7D2RD6f9YbcGXl2-RRvcHluTiLwWmt8LsRaaeICfEdkwgdwYwpP_”类型的下载地址会出现的bug

7.2023.04.05

抖音对selenium的访问进行了限制，需要进行手动验证。尝试了另外打开chrome进行remote连接，以及stealth.min.js两种方式均未解决；目前暂时增加了30秒延时。用户需要在30秒内手动进行验证，后面可以正常运行。

8.2023.04.18

部分之前可以用的用户地址，一段时间后会变为用户不存在，针对此种情况，采取跳过该用户的方式。

9.2023.07.29

add the "execute_script" process after page has been loaded, to acquire the real web content, and to get the web address of video and picture. 解决部分情况下图片或视频不能下载的问题，实现稳定下载。

10. 2023.12.20

抖音的图片格式的文件地址发生了改变，由<img class="V5BLJkWV"  src=...> 变为 <img class="vtuVZlmn" src=...>，因此代码进行相应的更改和升级。


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

1、视频名称为视频IP加视频文字内容，个别情况下视频文件的文字描述存在获取失败的情况，此时获得的文件名缺乏文字内容

2、下载一定数量网页后，会触发验证机制。目前尚未实现自动验证功能，需要手动验证。增加了延时，但未彻底解决。


五、后续完善工作

1、抖音的这种格式的用户页面 https://v.douyin.com/(user_id) ，user_id不唯一，如 https://v.douyin.com/67PUYbc/ 和 https://v.douyin.com/67PxFxtz 指向同一个用户;相同用户不同时刻获取的user_id不同，并且相近时刻获得的多个用户的user_id相近。暂不清楚原理，感觉在动态分配。后续可能要用转向的这个格式的网址：https://www.douyin.com/user/MS4wLjABAAAAkbkysgHQdweVnxzvTa423Csx3aWIlq5B3n1ApGRHBvA

3、对seleninum的反爬虫验证机制的，反反爬虫手段？

4、2023.04.18发现部分网页使用原来的下拉刷新的方式会提示刷新失败，需要手动刷新，因此不能获得全部视频和图片，后续看能否程序触发刷新动作。

