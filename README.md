# 使用方式



## 环境以及安装
**win10** **python** 
1、点击下面这个网页，安装miniconda也就是安装python，下载好以后安装即可，在安装时需要加入到系统环境变量，勾选下图第二个框即可。 <br>[https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py310_23.3.1-0-Windows-x86_64.exe](https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py310_23.3.1-0-Windows-x86_64.exe)<br>
 <img src="./showimg/miniconda.png" width="60%"/><br>



2、新建conda虚拟环境

在当前目录下打开终端

```
conda env create -f environment.yml
```



3、启用虚拟环境

```
conda activate zhihu
```



## 登录

运行以下内容，这一步是**手动**操作，需要人工输入账号和密码，然后点击登录就行，登录以后会自动保存好cookie，以后爬取时就不用重复登录了，保存的cookie在这个目录的**cookie**，产生的档案是**cookie_zhihu.pkl**<br>
 <h3><code><b style="color:#7a3e9d;">python crawler.py </b></code></h3>
<span style="color:#7a3e9d;">运行以后会弹出一个浏览器，自动打开知乎页面以后就可以开始登录，下图所示就是登录页面，两类登录方式都可以，只要能登录就行，<a style="color:black;"><b>点击登录以后，不要再操作页面，键盘或鼠标都不可以，登录以后查看目录cookie是否保存好cookie_zhihu.pkl，保存好就会开始爬取了。</b></a></span>
<br>
<img src="./showimg/login.png" width="29%"/>



## 爬取专栏文章列表

### 获取专栏HTML

随便使用一个浏览器，打开知乎网页**手动**搜索，关键词搜索专栏。

![image-20250402215325681](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250402215325681.png)

点击`F12`或者右键选择`检查`，打开开发者模式，选择选中元素模式：

![image-20250402215525851](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250402215525851.png)

点击这个按钮：

![image-20250402215542004](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250402215542004.png)

选择恰好能包含列表中所有搜索结果的部分：

![image-20250402215729006](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250402215729006.png)

会发现右侧自动跳转到该元素的代码部分：

![image-20250402215802077](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250402215802077.png)

右键，Copy，Copy outerHTML：

![image-20250402215914254](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250402215914254.png)



打开getColumnHref.py，将复制的文字粘贴在第29行，赋值给html_string变量：

![image-20250402220454301](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250402220454301.png)

打开命令行，执行该脚本：

```
python .\getColumnHref.py
```

![image-20250402220716299](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250402220716299.png)

可以发现zhuanlan_links.txt中更新了相应的专栏url

![image-20250402220822730](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250402220822730.png)



### 获取专栏中的文章和问题url

```
python .\crawler.py --column
```

![image-20250402221136113](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250402221136113.png)

等候浏览器自动爬取结束，可以看到zhuanlan_article_links.txt和zhuanlan_answer_links.txt已经更新了相应的url

![image-20250402221319157](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250402221319157.png)

![image-20250403181142758](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250403181142758.png)



## 爬取Topic文章列表

### 获取Topic的HTML

类似于专栏，复制元素的outerHTML

![image-20250403180522705](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250403180522705.png)

粘贴到getTopicHref.py的第29行：

![image-20250403180644974](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250403180644974.png)

执行命令：

```
python getTopicHref.py
```

![image-20250403180734494](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250403180734494.png)

点击回车，可以看到已经更新了链接：

![image-20250403180827754](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250403180827754.png)



### 获取Topic中的文章和问题url

执行命令：

```
python getUrlByTopic.py
```

![image-20250403181050619](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250403181050619.png)

等待执行完毕，可以看到已经更新到了topic_article_links.txt和topic_question_links.txt中

![image-20250408103247885](https://raw.githubusercontent.com/davidChouccccc/image/main/img/image-20250408103247885.png)


## 获取文章内容

从以上部分获取的文章链接（不管是专栏文章链接还是topic文章链接都一样）全文复制到article文件夹下的article.txt文件中，之后执行以下代码：

```
python .\crawler.py --article
```

等待代码执行即可



## 获取问题内容

从以上部分获取的问题链接（不管是专栏问题链接还是topic问题链接都一样）全文复制到answer文件夹下的answer.txt文件中，之后执行以下代码：

```
python .\crawler.py --answer
```

等待代码执行即可



### 注意
1、需要较好的网速，本机网速测验是下载100Mbps，上传60Mbps，低点也可以的，不是太慢太卡就行[https://www.speedtest.cn/](https://www.speedtest.cn/)<br>
2、爬取时设置了睡眠时间, 避免给知乎服务器带来太大压力，可以日间调试好，然后深夜运行爬取人少, 给其他小伙伴更好的用户体验, 避免知乎顺着网线过来找人，默认**6**s<br>
3、若是一直停在登录页面，可能是之前保存的cookie失效了，需要再次登录保存cookie


