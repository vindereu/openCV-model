# openCV-model
openCV常用繁雜功能模組化
# 穩定版本:
ROS noetic <br>
OpenCV 4.2.0

# 注意事項
除hsv_detect內滑鼠按鍵返回值可能因版本關係而不同，
其他檔案基本上在其他版本也可運行

# 安裝方式
  1. `cd <workspace_path>/src`

  2. `git clone https://github.com/vindereu/openCV-model.git`

  3. `source ../devel/setup.bash`

  4. `rospack list | grep cv_py`

&emsp;假如上一步有cv_py出現<br>
&emsp;5. `rosdep install cv_py`

  6. `catkin_make`

# IDE路徑設定(勿用~符號)
<套件絕對路徑>/cv_py/src

# 範例檔案使用(ROS)
rosrun cv_py <檔案>

# 引用說明
不需要引用內部檔案，引用cv_py後即可用各內部檔案所定義函式

`import cv_py`

若要用Trackbar <br>
`cv_py.Trackbar`

若要用slice <br>
`cv_py.slice`
