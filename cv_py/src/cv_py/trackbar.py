#!/usr/bin/env python3
import cv2 as cv
from enum import IntEnum
from typing import Sequence

class Trackbar:
    """
        功能:
        1. 拉條一次性快速創建.
        2. 拉條數值為字典結構, 方便理解得到的數值是什麼.
        3. 可將多個拉條群組化, 相關數值一次取得.
        4. 可進行簡單的拖曳範圍限制.
        5. 可一次重置所有拉條位置.

        獲取數值方式:
        已知情況: HSV = Trackbar(......)\n
        HSV.values(<拉條名/群組名>)

        目前缺點:
        1. 限制功能僅限對特定數值和跟指定拉條比大小, 無奇偶數刻度和
           自定義刻度數值.
        2. 限制設定無法一條函式設定多個拉條.
        3. 群組設定無法一條函式設定多個群組.
    """
    class LimitMode(IntEnum):
        '''
            用途:
            限制模式的整數枚舉類型變數宣告.

            呼叫用法:
            已知情況: HSV = Trackbar(...)\n
            HSV.LimitMode.LIMIT_GREATER\n
            TRACKBAR.LimitMode.LIMIT_GREATER
        '''
        LIMIT_GREATER = 0
        LIMIT_LESS = 1

    def __init__(self, window_name_: 'str', bar_name_: 'str | Sequence',
                 bar_init_: 'int | Sequence', bar_count_: 'int | Sequence'):
        '''
            用途:
            拉條資料初始化.

            參數 window_name_: 視窗名稱.
            參數 bar_name_: 拉條名稱, 數量可為一個或多個.
            參數 bar_init_: 拉條初始值, 數量可為一個或多個.
            參數 bar_count_: 拉條刻度最大值, 數量可為一個或多個.

            注意事項:
            除了參數window_name_, 其他參數之數量需保持一致.
        '''
        if not isinstance(window_name_, str):
            raise TypeError(f"Window name type is str, not {type(window_name_)}")

        isSequence = True
        isSingle = True
        for param in (bar_name_, bar_init_, bar_count_):
            if not isinstance(param, Sequence):
                isSequence = False
            elif not isinstance(param, (int, str)):
                isSingle = False
        
        if not (isSequence or isSingle):
            raise TypeError("All types of the last 3 params should be single element or Sequence.")

        if isSingle:
            for param, type_ in zip((bar_name_, bar_init_, bar_count_), (str, int, int)):
                if not isinstance(param, type_):
                    raise TypeError("Incorrect trackbar data type")
            
            self.__bar_name: 'tuple[str]' = (bar_name_,)
            self.__bar_value: 'dict[str, int]' = {bar_name_: bar_init_}
            self.__bar_count: 'dict[str, int]' = {bar_name_: bar_count_}
            self.__bar_reset: 'dict[str, int]' = {bar_name_: bar_init_}

        else:
            if len(bar_name_) != len(bar_init_) or len(bar_name_) != len(bar_count_):
                raise ValueError("Inconsistent amount of input data")
            for name, init, count in zip(bar_name_, bar_init_, bar_count_):
                temp_type = type(name), type(init), type(count)
                if temp_type != (str, int, int):
                    raise TypeError("Incorrect trackbar data type")
                if bar_name_.count(name) != 1:
                    raise ValueError("Duplicate trackbar name")
            
            self.__bar_name: 'tuple[str]' = tuple(bar_name_)
            self.__bar_value: 'dict[str, int]' = dict(zip(bar_name_, bar_init_))
            self.__bar_count: 'dict[str, int]' = dict(zip(bar_name_, bar_count_))
            self.__bar_reset: 'dict[str, int]' = dict(zip(bar_name_, bar_init_))
        
        self.__bar_limit: 'dict[str, tuple[int, int, str]]' = {}
        self.__bar_tick: 'dict[str, tuple[int]]' = {}
        self.__bar_last: 'dict[str, int]' = {}
        self.__window_name: 'str' = window_name_
        self.__group: 'dict[str, tuple[str]]' = {}
        self.__group_value: 'dict[str, tuple[int]]' = {}
        self.__done_build: 'bool' = False
        self.__build()

    def __build(self):
        '''
            用途:
            視窗和拉條建立.
        '''
        cv.namedWindow(self.__window_name)
        for name in self.__bar_name:
            cv.createTrackbar(name, self.__window_name, self.__bar_value[name],
                              self.__bar_count[name], self.__track)
        self.__done_build = True

    def __limit(self):
        '''
            用途:
            執行拉條的限制.

            運作方式:
            1. 查看有哪些被限制的拉條, 並檢查是否有跟其他拉條比較.
            2. 若拉條數值越過限制, 就重設拉條位置至限制數值之前一格.

            原始碼編輯注意:
            勿將實現方式(尤其是cv.setTrackbarPos)放於__track內,
            即可能導致__track無限遞迴直到超過Python遞迴限制, 並結束程式.
        '''
        if not self.__bar_limit:
            return

        for name in self.__bar_limit:
            mode, value, compare = self.__bar_limit[name]
            if mode == self.LimitMode.LIMIT_GREATER \
            and self.__bar_value[name]-value <= self.__bar_value[compare]:
                if self.__bar_value[name] == self.__bar_count[name]:
                    cv.setTrackbarPos(compare, self.__window_name,
                                        self.__bar_value[name] - 1)
                else:
                    cv.setTrackbarPos(name, self.__window_name,
                                        self.__bar_value[compare] + value)

            elif mode == self.LimitMode.LIMIT_LESS \
            and self.__bar_value[name]+value >= self.__bar_value[compare]:
                if self.__bar_value[name] == 0:
                    cv.setTrackbarPos(compare, self.__window_name, 1)
                else:
                    cv.setTrackbarPos(name, self.__window_name,
                                        self.__bar_value[compare] - value)
    
    def __skip(self):
        if not self.__bar_tick:
            return
        
        for name, last in self.__bar_last.items():
            if self.__bar_value[name] > last:
                index = self.__bar_tick[name].index(last)
                if index < len(self.__bar_tick[name]) - 1:
                    value = self.__bar_tick[name][index+1]
                    self.change_value(name, value)
                    self.__bar_last[name] = value
            elif self.__bar_value[name] < last:
                index = self.__bar_tick[name].index(last)
                if index > 0:
                    value = self.__bar_tick[name][index-1]
                    self.change_value(name, value)
                    self.__bar_last[name] = value

    def __track(self, pos_: 'int'):
        '''
            用途:
            openCV拉條的回調函數, 獲取拉條數值.

            參數 pos_: 拉條更新值, 無應用.

            運作方式:
            1. 獲取各拉條之數值, 並存進self.bar_value中.
            2. 若有創建群組, 則獲取成員數值, 並存進self.__group_value中.

            原始碼編輯注意:
            1. 若去除self.__done_build, 根據不同的運行速度, 在拉條創建
               到一定數量時, 後續拉條的初始值將固定設為0.
            2. 勿將會觸發__track()的函式放進__track()內.
        '''
        if self.__done_build:
            for name in self.__bar_name:
                self.__bar_value[name] = cv.getTrackbarPos(name, self.__window_name)
            if self.__group:
                for group_name in self.__group:
                    member_value = []
                    for member in self.__group[group_name]:
                        member_value.append(self.__bar_value[member])
                    self.__group_value[group_name] = tuple(member_value)

    def change_value(self, name_: 'str | Sequence', value_: 'int | Sequence'):
        '''
            用途:
            更改拉條的位置.

            參數 name_: 已創建的拉條名稱或群組名稱, 數量可為一個
                        或多個, 若名稱為群組名, 考慮的將是群組成員.
            參數 value_: 拉條更改成的數值, 數量可為一個多個, 元組維度最多2維.

            注意事項:
            確保name_和value_各元素都有伴, 參見運作方式.

            範例用法:
            已知情況: "min": ("Hmin", "Smin", "Vmin").
            change_value("Hmin", 0)\n
            change_value(("Hmin", "Smin"), 0)\n
            change_value("min", 0)\n
            change_value("min", (10, 5, 11))

            運作方式:
            (以下將name_和value_簡稱name和v)
            1. 若name為字串或元組, v為整數, 則將所有與name相關拉條之
               數值更改為v.
            2. 若name為群組名或元組, v為元組, 則將群組成員名或元組內之
               字串與v內的數值一一對應, 並進行數值更改.
        '''
        if isinstance(name_, str):
            if name_ in self.__group:
                if isinstance(value_, int):
                    for name in self.__group[name_]:
                        cv.setTrackbarPos(name, self.__window_name, value_)

                elif isinstance(value_, Sequence):
                    if len(self.__group[name_]) != len(value_):
                        raise ValueError("Inconsistent amount of input data")
                    for name, value in zip(self.__group[name_], value_):
                        cv.setTrackbarPos(name, self.__window_name, value)

                else:
                    raise TypeError("Value type must be int or Sequence")

            elif name_ in self.__bar_name:
                if not isinstance(value_, int):
                    raise TypeError("Value type should be int")
                cv.setTrackbarPos(name_, self.__window_name, value_)

            else:
                raise ValueError(f"Name {name_} doesn't exist")

        elif isinstance(name_, Sequence):
            if isinstance(value_, int):
                for name in name_:
                    self.change_value(name, value_)

            elif isinstance(value_, Sequence):
                if len(value_) != len(name_):
                    raise ValueError("Inconsistent amount of input data")
                for name, value in zip(name_, value_):
                    self.change_value(name, value)

        else:
            raise TypeError("Name type must be str or Sequence")

    def print_values(self, output_name_: 'str | Sequence' = None):
        '''
            用途:
            將數值與其所屬名稱在命令行印出, 格式為先印出拉條再印出群組.

            參數 output_name_: 要輸出的拉條名稱或群組名稱, 數量可為一
                               個或多個. 若未指定, 則印出所有拉條和群
                               組的名稱與數值.
        '''
        text = ""
        if isinstance(output_name_, str):
            text = text + "\'" + output_name_ + "\': "
            if output_name_ in self.__bar_name:
                text = text + str(self.__bar_value[output_name_])
            elif output_name_ in self.__group:
                text = text + str(self.__group_value[output_name_])
            else:
                raise ValueError(f"Name {output_name_} doesn't exist")
            print("="*len(text))
            print(text)
            print("="*len(text))
            return

        if isinstance(output_name_, Sequence):
            for name in output_name_:
                if not isinstance(name, str):
                    raise TypeError("Type of output name must be Sequence and includes str")
                if name not in self.__bar_name and name not in self.__group:
                    raise ValueError(f"Name {name} doesn't exist")

            for name in output_name_:
                if name in self.__bar_name:
                    text = text + "\'" + name + "\': "
                    text = text + str(self.__bar_value[name]) + "  "

            if text:
                text = text[:-2] + '\n'
            index = len(text) - 1
            for name in output_name_:
                if name in self.__group:
                    text = text + "\'" + name + "\': "
                    text = text + str(self.__group_value[name]) + "  "

            if len(text)-1 == index:
                text = text[:-1]
            else:
                text = text[:-2]

        elif output_name_ is None:
            for name in self.__bar_name:
                text = text + "\'" + name + "\': "
                text = text + str(self.__bar_value[name]) + "  "

            if text:
                text = text[:-2] + '\n'
            index = len(text) - 1
            for name in self.__group:
                text = text + "\'" + name + "\': "
                text = text + str(self.__group_value[name]) + "  "

            if len(text)-1 == index:
                text = text[:-1]
            else:
                text = text[:-2]

        print("="*max((index, len(text)-index-1)))
        print(text)
        print("="*max((index, len(text)-index-1)))

    def reset(self) -> None:
        '''
            用途:
            將拉條數值重置至設定值.

            注意事項:
            勿無間斷呼叫, 否則無法拉動拉條.

            運作方式:
            呼叫change_value(), 並將重置名稱和數值代入.
        '''
        for name, value in zip(self.__bar_reset, self.__bar_reset.values()):
            self.change_value(name, value)

    def _set_even_tick(self, start: int, end: int):
        '''
            ===== 未完成 =====

            用途:
            將拉條設定為偶數刻度

            參數 start: 起始數值
            參數 end: 終止數值
        '''
        pass

    def set_group(self, group_name_: 'str', member_name_: 'Sequence[str]'):
        '''
            用途:
            將多個拉條歸納成一個群組, 方便後續一次取得相關數值.

            參數 group_name_: 群組名稱.
            參數 member_name_: 已創建的拉條名稱元組, 元素數量至少2個.

            注意事項:
            1. 禁止玩俄羅斯娃娃, 函式已有名稱和類別限制.
            2. 若存在的拉條數量只有一個, 此群組功能將不啟用.
            3. 不要重複創建同一個群組.

            範例用法:
            已知情況: "Hmin", "Smin", "Vmin"\n
            set_group("min", ("Hmin", "Smin", "Vmin"))

            運作方式:
            將輸入參數放進字典, 並呼叫__track()一次以更新群組數值,
            後續運作請參考原始碼裡的__track().

            原始碼編輯注意:
            避免改成俄羅斯娃娃遊戲, 我還沒試過, 但若照__track()的運行邏輯,
            且語法正確的話, 我可以猜想到你的__track()很可能會玩物喪志.
            但還是祝你順利.
        '''
        if len(self.__bar_name) == 1:
            raise Exception("Only one trackbar, no support for group creation")
        if not isinstance(member_name_, Sequence):
            raise TypeError("Member name type must be Sequence and include str")
        if len(member_name_) == 1:
            raise ValueError("Number of members must be greater than 1")
        for name in member_name_:
            if name not in self.__bar_name:
                raise ValueError(f"Name {name} doesn't exist")

        if not isinstance(group_name_, str):
            raise TypeError("Group name type must be str")
        if group_name_ in self.__group:
            raise ValueError(f"Can't create group: \"{group_name_}\" again")
        if group_name_ in self.__bar_name:
            raise ValueError("Group name conflicts with trackbar name")

        self.__group[group_name_] = tuple(member_name_)
        self.__track(0)

    def set_limit(self, bar_name_: 'str', mode_: 'int', value_: 'int',
                  bar_compare_: 'str' = ""):
        '''
            用途:
            設定拉條的拖動範圍, 可用在ROI的大小限制或是kernel大小等...

            參數 bar_name_: 已創建的拉條名稱.
            參數 mode_: 限制模式, 可用模式為LimitMode裡的LIMIT_GREATER和LIMIT_LESS.
            參數 value_: 限制數值, 若bar_compare_被設定, 則是最小可相差的數值.
            參數 bar_compare_: 被參考的拉條名稱, 可不設定.

            注意事項:
            拉條數值不會超過或等於設定的value_.

            運作方式:
            將輸入參數放進字典, 限制方式請參考__limit().
        '''
        if not isinstance(bar_name_, str):
            raise TypeError("Name type must be str")
        if bar_name_ not in self.__bar_name:
            raise ValueError(f"Name {bar_name_} doesn't exist")

        if not isinstance(mode_, int):
            raise TypeError("Mode type must be int or IntEnum")
        if mode_ not in [self.LimitMode.LIMIT_GREATER, self.LimitMode.LIMIT_LESS]:
            raise ValueError

        if not isinstance(bar_compare_, str):
            raise TypeError("Compare type must be str")
        if bar_compare_ != "" and bar_compare_ not in self.__bar_name:
            raise ValueError("The trackbar name to compare does not exist")

        if not isinstance(value_, int):
            raise TypeError("Value type must be int")
        
        if bar_compare_:
            self.__bar_limit[bar_name_] = (mode_, value_, bar_compare_)
        elif mode_ == self.LimitMode.LIMIT_GREATER:
            cv.setTrackbarMin(bar_name_, self.__window_name, value_ + 1)
        elif mode_ == self.LimitMode.LIMIT_LESS:
            cv.setTrackbarMax(bar_name_, self.__window_name, value_ - 1)

    def _set_odd_tick(self, start: int, end: int):
        '''
            ===== 未完成 =====

            用途:
            將拉條設定為奇數刻度

            參數 start: 起始數值
            參數 end: 終止數值
        '''

    def set_reset_value(self, name_: 'str | Sequence', value_: 'int | Sequence'):
        '''
            用途:
            設定拉條的重置數值, 若沒呼叫此函式, 則重置數值為拉條創建之
            初始值.

            參數 name_: 已創建的拉條名稱或是群組名稱. 數量可為一個
                            或多個, 若名稱為群組名, 考慮的將是群組成員.
            參數 value_: 重置數值, 數量可為一個多個, 元組維度最多2維.

            注意事項:
            1. 確保name_和value_各元素都有伴, 參見運作方式.
            2. 之後要啟動重置時需呼叫reset().

            範例用法:
            已知情況: "min": ("Hmin", "Smin", "Vmin").\n
            set_reset_value(("Hmin", "Smin", "Vmin"), 90)\n
            set_reset_value(("Hmin", "Smin", "Vmin"), (3, 31, 15))\n
            set_reset_value("min", 0)\n
            set_reset_value("min", (20, 1, 2))\n
            set_reset_value(("min", "Hmin"), ((0, 1, 2), 50))

            運作方式:
            (以下將name_和value_簡稱name和v)
            1. 若name為字串或元組, v為整數, 則設定所有與name相關拉條之
               重置數值為v.
            2. 若name為群組名或元組, v為元組, 則將群組成員名或元組內之
               字串與v內的數值一一對應, 並進行重置數值設定.
        '''
        if isinstance(name_, str):
            if name_ in self.__group:
                if isinstance(value_, int):
                    for name in self.__group[name_]:
                        self.__bar_reset[name] = value_

                elif isinstance(value_, Sequence):
                    if len(value_) != len(self.__group[name_]):
                        raise ValueError("Inconsistent amount of input data")
                    for name, value in zip(self.__group[name_], value_):
                        self.__bar_reset[name] = value

                else:
                    raise TypeError("Value type must be int or Sequence")

            elif name_ in self.__bar_name:
                if not isinstance(value_, int):
                    raise TypeError("Value type should be int")
                self.__bar_reset[name_] = value_

            else:
                raise ValueError(f"Name {name_} doesn't exist")

        elif isinstance(name_, Sequence):
            if isinstance(value_, int):
                for name in name_:
                    self.set_reset_value(name, value_)

            elif isinstance(value_, Sequence):
                if len(value_) != len(name_):
                    raise ValueError("Inconsistent amount of input data")
                for name, value in zip(name_, value_):
                    self.set_reset_value(name, value)

            else:
                raise TypeError("Value type must be int or Sequence")

        else:
            raise TypeError("Name type must be str or Sequence")

    def _set_tick(self, name: str, *tick: int):
        '''
            ===== 未完成 =====

            用途:
            將拉條設定為指定刻度序列數值

            參數 name: 拉條名稱
            參數 tick: 刻度值
        '''
        if name not in self.__bar_name:
            raise ValueError(f"Name {name} doesn't exist")

        tick = sorted(list(set(tick)))
        self.__bar_tick[name] = tick
        if self.__bar_value[name] not in tick:
            self.__bar_last[name] = tick[0]
            self.change_value(name, tick[0])
        
        else:
            self.__bar_last[name] = self.__bar_value[name]

        self.set_limit(name, self.LimitMode.LIMIT_GREATER, tick[0] - 1)
        self.set_limit(name, self.LimitMode.LIMIT_LESS, tick[-1] + 1)
        
    def values(self, name_: 'str') -> 'int | tuple':
        '''
            用途:
            返回需要的拉條數值

            參數 name_: 已創建的拉條名稱或群組名稱, 若是拉條名稱,
                        則返回型態為整數. 若是群組名稱, 則返回型態
                        為元組.

            注意事項:
            若要印出或查看數值, 建議使用print_values().
        '''
        if not isinstance(name_, str):
            raise TypeError("Name type must be str")
        self.__skip()
        self.__limit()

        if name_ in self.__bar_name:
            return self.__bar_value[name_]
        if name_ in self.__group:
            return self.__group_value[name_]
        raise ValueError(f"Name {name_} doesn't exist")
