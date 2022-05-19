# openCV-model
openCV常用繁雜功能模組化
# 穩定版本:
ROS noetic
OpenCV 4.2.0

除hsv_detect內滑鼠按鍵返回值可能因版本關係而不同，
其他檔案基本上在其他版本也可運行



# 安裝方式
1. `cd <workspace_path>/src`
2. `git clone
3. `source ../devel/setup.bash`
4. `rospack list | grep cv_py`

4. `rosdep install cv_py`

5. `catkin_make`



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
