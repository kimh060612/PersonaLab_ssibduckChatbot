import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--conversation', help=' : Please enter the conversation', default="내 이름은 나츠키 스바루! 천하 제일 무일푼의 한량이다!")
args = parser.parse_args() 
print(args.conversation)