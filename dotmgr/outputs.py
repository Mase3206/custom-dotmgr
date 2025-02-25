#!/usr/bin/env python3.12


ANSI_GREEN = '\\e[32m'
ANSI_BLUE = '\\e[34m'
ANSI_CYAN = '\\e[36m'
ANSI_RED = '\\e[31'
ANSI_RESET = '\\e[0m'

def header(text: str):
	print('\n\n' + 
	   	ANSI_GREEN + '========  ' + text + '  ========' + ANSI_RESET
		+ '\n')
	
def subheader(text: str):
	print('\n' +
		ANSI_BLUE + '----  ' + text + '  ----' + ANSI_RESET)
	
def step(text: str):
	print(ANSI_CYAN + '- ' + text)

def bad(step_text: str, status_text: str):
	print(step_text + ': ' +
		ANSI_RED + status_text + ANSI_RESET)

def good(step_text: str, status_text: str):
	print(f'{step_text}: {status_text}')


if __name__ == '__main__':
	exit(1)
