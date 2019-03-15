# step 1
## 进入项目目录
```shell
cd weibo_product
```
## 进行数据迁移
```shell
python manage.py migrate
```
# setp 2 
## 运行项目
```shell
python manage.py runserver 127.0.0.1:3999
```
# setp 3
### 进入script.py 页面---->找到136行和143行进行修改
```python
# 输入用户名
e_username.send_keys("你的微博账号")
 # 输入密码
e_password.send_keys('你的微博密码')
```
# setp 4
## 完成第三步以后就进行数据爬取
```shell
python script.py 
```
# setp 5
## 复制下面的网址查看效果
```python
http://127.0.0.1:3999/
```
