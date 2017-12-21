# coding: utf-8

"""命令行教务处

Usage:
    tickets [-skti] <student_number> <password>

Options:
    -h,--help   显示帮助菜单
    -s          成绩
    -k          考试信息
    -t          课表
    -i          评教
Example:
    getscore_1 -k 1120161174 222222
    getscore_1 -s 1120161174 222222
"""

from bit_jwc_login import *
from prettytable import PrettyTable
from prettytable import from_html
from docopt import docopt
import time
import pandas as pd

#成绩制表
def pretty_print_1(scores):
    x = PrettyTable()
    x._set_field_names(scores[-1])
    scores.pop(-1)
    for score in scores:
        new = []
        for i in score:
            i = i.encode('utf-8')
            i = i.decode('utf-8')
            new.append(i)
        x.add_row(new)
    print(x)

def pretty_print_2(exams):
    x = PrettyTable()
    x._set_field_names(exams[0])
    for exam in exams:
        new = []
        for i in exam:
            i = i.encode('utf-8')
            i = i.decode('utf-8')
            new.append(i)
        x.add_row(new)
    print(x)

def main():
    """command-line interface"""
    arguments = docopt(__doc__)
    student_number = arguments['<student_number>']
    password = arguments['<password>']
    time.clock()
    if arguments['-s'] is True:
        print('历年成绩:')
        pretty_print_1(getGradefromsoup(jwclogin(student_number, password,'-s')))
    if arguments['-k'] is True:
        print('考试信息：')
        pretty_print_2(getExaminformation(jwclogin(student_number,password,'-k')))
    if arguments['-i'] is True:
        print('开始评教')
        jwclogin(student_number,password,'-i')

if __name__ == '__main__':
    main()