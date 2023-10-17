# A simple GPT chat interface with customizable API
这只是作为一个个人学习中小项目的记录，但该有的功能基本较完善，所以便想着上传到GitHub


chat.py为源码文件

如果想使用的话下载以后可以打开chat.exe直接运行，但同时需要让fileConfig.json文件与程序在同一个文件夹下

fileConfig文件是作为程序的配置文件使用


另外测试时发现不经过设置似乎无法使用系统代理，如果是用的v2rayN的话，可以通过以下设置解决：

依次打开“设置”——“参数设置”——“系统代理设置”——“高级代理设置”，将其更改为“http=http://{ip}:{http_port};https=http://{ip}:{http_port}”选项


测试时我没有自己搭建代理服务，所以如果您发现在该方面有bug，欢迎提出

该项目只是我在学习过程中一时兴起开发的，开发周期也很短，肯定有诸多不良之处，所以本意也只是作为一个学习记录
