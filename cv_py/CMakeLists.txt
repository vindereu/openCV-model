cmake_minimum_required(VERSION 3.0.2)
project(cv_py)

find_package(catkin REQUIRED COMPONENTS
)

catkin_python_setup()

catkin_package()

include_directories(
  ${catkin_INCLUDE_DIRS}
  ${OpenCV_INCLUDE_DIRS}
)

catkin_install_python(PROGRAMS
  script/bar
  script/filter_test
  script/hsv_detect
  script/line_detect
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)