# -*- coding: utf-8 -*-

import socket
import sys
import select

SERVER_PORT = 5005
SERVER_IP   = '192.168.56.101'

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

# o select quer ficar a espera de ler o socket e ler do stdin (consola)
inputs = [sock, sys.stdin]

#FUNCOES DE CADA OPERACAO
def acknowledge(dest):
  respond_msg = "OK " + dest + "\n"
  sock.sendto(respond_msg.encode(), (SERVER_IP, SERVER_PORT)) 

def replyInvitation(sender, to, reply):

  if reply == "Y\n":
	 msg = "INVR " + sender + " " + to + " accept"
	 sock.sendto(msg.encode(), (SERVER_IP,SERVER_PORT))

  else:
	 msg = "INVR " + sender + " " + to + " reject"
	 sock.sendto(msg.encode(), (SERVER_IP,SERVER_PORT))

def readList(msg):
  i=0
  aux=""
  print "Message received from server:"
  print "LSTR:"
  while i < len(msg):
	 aux=aux+msg[i]
	 if msg[i] == ";":
		print aux
		aux=""
	 i+=1

#TIC TAC TOE
def drawBoard(board):
	# This function prints out the board that it was passed.

	 # "board" is a list of 10 strings representing the board (ignore index 0)    print('   |   |')
	 print(' ' + board[1] + ' | ' + board[2] + ' | ' + board[3])
	 #print('   |   |')
	 print('---+---+---')
	 #print('   |   |')
	 print(' ' + board[4] + ' | ' + board[5] + ' | ' + board[6])
	 #print('   |   |')
	 print('---+---+---')
	 #print('   |   |')
	 print(' ' + board[7] + ' | ' + board[8] + ' | ' + board[9])
	 #print('   |   |')

def makeMove(board, letter, move):
	if ord(move) <= 57 and ord(move) > 48:  #ascii para os valores entre 1 e 9
		if board[int(move)] == " ":
		 	board[int(move)] = letter
		 	return True
		else:
			print "Try again, invalid position"
			return False
	else:
			print "Try again, invalid position"
			return False

def isWinner(bo, le):
	 # Given a board and a player's letter, this function returns True if that player has won.
	 # We use bo instead of board and le instead of letter so we don’t have to type as much.
	 return ((bo[7] == le and bo[8] == le and bo[9] == le) or # across the top
	 (bo[4] == le and bo[5] == le and bo[6] == le) or # across the middle
	 (bo[1] == le and bo[2] == le and bo[3] == le) or # across the bottom
	 (bo[7] == le and bo[4] == le and bo[1] == le) or # down the left side
	 (bo[8] == le and bo[5] == le and bo[2] == le) or # down the middle
	 (bo[9] == le and bo[6] == le and bo[3] == le) or # down the right side
	 (bo[7] == le and bo[5] == le and bo[3] == le) or # diagonal
	 (bo[9] == le and bo[5] == le and bo[1] == le)) # diagonal

def getBoardCopy(board):
	 # Make a duplicate of the board list and return it the duplicate.
	 dupeBoard = []

	 for i in board:
		  dupeBoard.append(i)

	 return dupeBoard

def isSpaceFree(board, move):
	 # Return true if the passed move is free on the passed board.
	 return board[move] == ' '

def isBoardFull(board):
	 # Return True if every space on the board has been taken. Otherwise return False.
	 for i in range(1, 10):
		 if isSpaceFree(board, i):
				return False
	 return True



#CORPO PRINCIPAL
flag = 0

while True:

	if flag == 1:
		drawBoard(theBoard)
		flag=0

	print("Input message to server below:")
	ins, outs, exs = select.select(inputs,[],[])
	#select devolve para a lista ins quem esta a espera de ler
	for i in ins:
		# i == sys.stdin - alguem escreveu na consola, vamos ler e enviar
		if i == sys.stdin:
			# sys.stdin.readline() le da consola
			msg = sys.stdin.readline()
			arg = msg.split()
			
			if arg[0] == "REG":
				name = arg[1]

			if arg[0] == "MOV":
				#msg = msg.split()
				move = arg[1]
				if gameIsPlaying:
					if turn == 'yourTurn':

						if makeMove(theBoard, player1Letter, move):
							flag=1
							msg = arg[0]+" "+name+" "+oponent+" "+arg[1]
							if isWinner(theBoard, player1Letter):
								#ALTERAR
								drawBoard(theBoard)
								print('Hooray! You have won the game!')
								gameIsPlaying = False
								flag = 0
								msg = "END"+" "+name+" "+oponent+" "+arg[1]+" V"
						
							else:

								if isBoardFull(theBoard):
									drawBoard(theBoard)
									print('The game is a tie!')
									msg = "END"+" "+name+" "+oponent+" "+arg[1]+" D"
									flag = 0
									

								else:
									turn = 'notYourTurn'
									
						else:
							break

					else:
						print "Not your turn"
						break
	
			# envia mensagem da consola para o servidor
			sock.sendto(msg.encode(),(SERVER_IP,SERVER_PORT))
			# i == sock - o servidor enviou uma mensagem para o socket
		elif i == sock:
			(msg,addr) = sock.recvfrom(1024)
			sub = msg
			cmds = msg.split()
			if cmds[0] == "MOV":
				acknowledge(cmds[1])
				move=cmds[3]

				if gameIsPlaying:
					if turn == "notYourTurn":
						makeMove(theBoard, player2Letter, move)
						flag = 1

						if isWinner(theBoard, player2Letter):
							#ALTERAR
							drawBoard(theBoard)
							print('Uhhh!!!! What a shame. Better luck next time ;^)')
							gameIsPlaying = False
							flag=0
							break
						else:
							if isBoardFull(theBoard):
								drawBoard(theBoard)
								print('The game is a tie!')
								flag=0
								break
							else:
								turn = 'yourTurn'
								break

					else:
						print("Not your turn")
						break

			if cmds[0] == "LSTR:":
				acknowledge("server")
				readList(cmds[1])
				break

			if cmds[0] == "INV":
				acknowledge(cmds[1])
				print("Received invite from " + cmds[1])
				print("Type [Y] to accept or [N] to deny:")
				msg = sys.stdin.readline()

				if msg == "Y\n":
					turn='notYourTurn'
					theBoard = [' '] * 10
					player1Letter, player2Letter = ['O', 'X']
					gameIsPlaying = True
					flag = 1
					oponent = cmds[1]

				replyInvitation(cmds[2],cmds[1], msg)
				break

			if cmds[0] == "INVR":
				print("Player " + cmds[1] + " has " + cmds[2] + " your invitation")
				acknowledge(cmds[1])
				if cmds[2] == "accepted":
					oponent = cmds[1]
					theBoard = [' '] * 10
					player1Letter, player2Letter = ['X', 'O']
					turn="yourTurn"
					gameIsPlaying = True
					flag = 1
				break

			if cmds[0] == "END":
				acknowledge(cmds[1])
				move=cmds[3]

				makeMove(theBoard, player2Letter, move)

				if cmds[4] == "V":
					drawBoard(theBoard)
					print('Uhhh!!!! What a shame. Better luck next time ;^)')
					gameIsPlaying = False
					flag=0
					break

				else:
					drawBoard(theBoard)
					print('The game is a tie!')
					flag=0
					break

			if cmds[0] == "NOK:":
				print sub
				break
					

		
			print "Message received from server:", cmds[0]