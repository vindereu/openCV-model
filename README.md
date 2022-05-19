# openCV-model
openCV常用繁雜功能模組化
穩定版本:
ROS noetic
OpenCV 4.2.0

除hsv_detect內滑鼠按鍵返回值可能因版本關係而不同，
其他檔案基本上在其他版本也可運行



安裝方式
1. 將cv_py全部內容下載至工作區域的src資料夾內

2. source <workspace_path>/devel/setup.bash

3. rospack list | grep cv_py  # 確認有顯示cv_py

4. rosdep install cv_py  # 安裝套件所需依賴

5. catkin_make



IDE路徑設定(勿用~符號)
<套件絕對路徑>/cv_py/src



範例檔案使用
rosrun cv_py <檔案>



引用說明
不需要引用內部檔案，引用cv_py後即可用各內部檔案所定義函式

import cv_py

若要用Trackbar
cv_py.Trackbar

若要用slice
cv_py.slice
