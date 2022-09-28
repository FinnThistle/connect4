"""
TickTackToeAgainstComputer(graphical).py

A program implementing the minimax recurssive algorithm in
a tick-tack-toe setting. 

Most of this code is referenced from this website which is cited in my paper 
https://github.com/AlejoG10/python-tictactoe-ai-yt

minimax tree algorithm basis:

Let X be a human.
Let O be the computer.

The computer will span the tree of possible board positions 
looking at every posible situation where the game has ended;
in a draw (where the board is full and there is no winner),
where O wins, or where X wins.

If a board occurs where X wins, the computer will mark that specific
board as payoff = -1.

If a board occurs where O wins the computer will mark that specific
board as payoff = +1.

If a board occurs where the game ends in a tie, the computer will mark
that specific board as payoff = 0. 

If a board is not yet finnished the computer will look to the children
(the opponents move to their possible move) of that board, if the 
children have a finnished board state the computer will mark the board
with a number according to the information above.

If possible, this number will carry up the current state of the board, 
and it has a optimal response for anything the opponent plays.The computer
will choose the highest value out of the next immediate board positions 
and that is where it will make O's move.

After I got it woking I figured out something kind of pecular.
If the algorithim has multiple paths that will equal 1 it will
not prioritize winning in less moves, like a human would.

You can see this for yourself if you do the following three moves.

top-left
bottom-middle
top-middle

The algorithim will not 'throw-away' a win but it will not win at
the first imediate chance(in this example on the horizontal middle
connection).


Finn Thistle | May 2022
"""


bDebug = False #debug boolean

import sys
import pygame
import math
import copy #Used to make multiple saved copies of the board inside the reccursion(I tried to use tempBoard = board[:] but it wouldn't work)
from time import time
#CONSTANTS

width = 800
height = 800
rows = 3
columns = 3
squareSize = width/columns
bgColor = "gray"
lineColor = "white"
lineWidth = 10
O_Radius = 90
margin = 50
x = 'X'
o = 'O'
infinity = math.inf
#PYGAME INITIALIZATION
pygame.init()
screen = pygame.display.set_mode((width, height))
screen.fill(bgColor)
class Board:
    def __init__(self):
        self.squares = [[0 for r in range(3)] for i in range(3)] #A list of three lists, each with three elements
        self.totalMarkedSquares = 0

    def __str__(self):
        """Utility to print out board in terminal."""
        return f"{self.squares[0]}\n{self.squares[1]}\n{self.squares[2]}"
    def checkBoard(self):
        """
            will return 0 if game is not over
            will return 1 if player 1 wins
            will return 2 if player 2 wins
        """   
        #Verticle wins
        for col in range(columns):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                return self.squares[0][col] #will return a number assigned to one of the squares in that connection
        #Horizontal wins
        for row in range(rows):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                return self.squares[row][0] 
        #Diagnol wins
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] !=0:
            return self.squares[0][0]
        elif self.squares[0][2] == self.squares[1][1] == self.squares[2][0] != 0: 
            return self.squares[0][2]

        return 0 #otherwise return 0
    def markSquare(self, row, column, symbol):
        """Marks '.squares' as either 1 or 2 depending on which player went"""
        self.squares[row][column] = symbol
        self.totalMarkedSquares += 1

    def bEmptySquare(self, row, column):
        """Returns True if given position is empty"""
        return self.squares[row][column] == 0

    def bBoardFull(self):
        """Returns True if board is full"""
        return self.totalMarkedSquares==9

    def bGameOver(self):
        """Returns true if game has ended."""
        return self.bBoardFull() or self.checkBoard()

    def allOpenSquares(self):
        """Returns a list of remaining open spaces"""
        MTsquares = []
        for row in range(rows):
            for col in range(columns):
                if self.bEmptySquare(row, col):
                    MTsquares.append((row,col))
        return MTsquares
            
class BestmoveAlgorithm:
    def __init__(self):
        self.player = 2

    def miniMax(self, board, minimizing=False):
        """A recursive function that spans all possible boards and gives them the following payoff"""
        case = board.checkBoard()
        if case == 1: #If the human wins the specific board give the payoff -1
            return -1, None
        elif case == 2: #If the computer wins the specific board give the payoff +1
            return 1, None
        elif board.bBoardFull(): #If the game results in a tie give the payoff 0
            return 0, None
        
        #If the current board does not result in the game being over
        if minimizing:
            minPayoff = 2 #initialvalue to be rewritten as for loop is run
            bestMoveYet = None
            openSquaresList = board.allOpenSquares()
                                                    #NOTE vvCheck for coppied comments
            for (row, col) in openSquaresList:
                tempBoard = copy.deepcopy(board) #creates a copy of the board instead of a reference to it 
                tempBoard.markSquare(row, col, 1)
                tempPayoff = self.miniMax(tempBoard, False)[0] #Send to check the opponents move, or if the game has ended
                if tempPayoff < minPayoff: #find the best payoff and the square that yeilds that payoff.
                    minPayoff = tempPayoff
                    bestMoveYet = (row, col)
            return minPayoff, bestMoveYet
        else: #same as above code but inverse for opponent
            maxPayoff = -2 
            bestMoveYet = None
            openSquaresList = board.allOpenSquares()
            for (row, col) in openSquaresList:
                tempBoard = copy.deepcopy(board) 
                tempBoard.markSquare(row, col, 2)
                tempPayoff = self.miniMax(tempBoard, True)[0] 
                if tempPayoff > maxPayoff:
                    maxPayoff = tempPayoff
                    bestMoveYet = (row, col)
            return maxPayoff, bestMoveYet

    def miniMax_AlphaBeta(self, board, alpha, beta, minimizing=False):
        """A more effecient recursive function that spans all possible boards and gives them the following payoff"""
        case = board.checkBoard()
        if case == 1: #If the human wins the specific board give the payoff -1
            return -1, None
        elif case == 2: #If the computer wins the specific board give the payoff +1
            return 1, None
        elif board.bBoardFull(): #If the game results in a tie give the payoff 0
            return 0, None
        
        #If the current board does not result in the game being over
        if minimizing:
            minPayoff = 2 #initialvalue to be rewritten as for loop is run
            bestMoveYet = None
            openSquaresList = board.allOpenSquares()
                                                    #NOTE vvCheck for coppied comments
            for (row, col) in openSquaresList:
                tempBoard = copy.deepcopy(board) #creates a copy of the board instead of a reference to it 
                tempBoard.markSquare(row, col, 1)
                tempPayoff = self.miniMax_AlphaBeta(tempBoard, alpha, beta, False)[0] #Send to check the opponents move, or if the game has ended
                if tempPayoff < minPayoff: #find the best payoff and the square that yeilds that payoff.
                    minPayoff = tempPayoff
                    bestMoveYet = (row, col)
                if minPayoff < beta:
                    beta = minPayoff
                if alpha >= beta: 
                    break
            return minPayoff, bestMoveYet
        else: #same as above code but inverse for opponent
            maxPayoff = -2 
            bestMoveYet = None
            openSquaresList = board.allOpenSquares()
            for (row, col) in openSquaresList:
                tempBoard = copy.deepcopy(board) 
                tempBoard.markSquare(row, col, 2)
                tempPayoff = self.miniMax_AlphaBeta(tempBoard, alpha, beta, True)[0] 
                if tempPayoff > maxPayoff:
                    maxPayoff = tempPayoff
                    bestMoveYet = (row, col)
                if maxPayoff > alpha:   #keep track of alpha value for later iterations of minimax function, and reset it if aplicable
                    alpha = maxPayoff
                if alpha >= beta: # 'Prune' the tree (Breakout of the loop), as the best response to each of these  options have already been found
                    break
            return maxPayoff, bestMoveYet

    def bestMove(self, board):
        """Returns best move using the minimax algorithim."""
        payoff, bestmove = self.miniMax(board) 
        if bDebug:print("AI's move is square", bestmove, "it has a pay off of", payoff)
        return bestmove
class Game:
    def __init__(self):
        
        self.board = Board()
        self.computer = BestmoveAlgorithm()
        self.currentPlayer = 1
        self.bGameRunning = True
    def showLines(self):
        """Shows guiding lines."""
        # vertical lines
                        #(reference to screen,color, starting cord, ending cord, width of line)
        pygame.draw.line(screen, lineColor, (squareSize, 0), (squareSize, height), lineWidth)
        pygame.draw.line(screen, lineColor, (width-squareSize, 0), (squareSize*2, height), lineWidth)
        # horizontal lines
        pygame.draw.line(screen, lineColor, (0, squareSize), (width, squareSize), lineWidth)
        pygame.draw.line(screen, lineColor, (0, height-squareSize), (width, height-squareSize), lineWidth)
    def markSquareGraphic(self, row, column):
        """Marks the square with the designated symobol in the pygame window"""
        # Some clever code that figures out the position of the symbol on the graphical board based off of col and row 
        if self.currentPlayer == 1: #Draw an 'X'
    
            #going down line
            downStartPos = ( (column * squareSize) + margin, (row * squareSize) + margin)                     
            downEndPos = ( (column * squareSize) + squareSize-margin, (row * squareSize) +squareSize-margin)
            pygame.draw.line(screen, "red", downStartPos, downEndPos, lineWidth+4)
            #going up line
            upStartPos = ( (column * squareSize) + margin, (row * squareSize) + squareSize - margin)
            upEndPos = ( (column * squareSize)+squareSize-margin, (row * squareSize)+margin)
            pygame.draw.line(screen, "red", upStartPos, upEndPos, lineWidth+4)

        elif self.currentPlayer==2: #Draw an 'O'
            center = ( (column * squareSize) + (squareSize //2) , (row * squareSize) + (squareSize //2) )
            pygame.draw.circle(screen, "black", center, O_Radius, lineWidth)
    def makeMove(self, row, col):
        """Simulates an entire players move"""
        self.board.markSquare(row, col, self.currentPlayer)
        self.markSquareGraphic(row, col)
        self.nextPlayerTurn()
    
    def nextPlayerTurn(self):
        """Osolates between value one and two"""
        self.currentPlayer = self.currentPlayer % 2 + 1

def main():
    listOfTimePermoves = [] # for timing

    #make a game 
    game = Game()
    board = game.board
    computer = game.computer
    game.showLines()
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and game.bGameRunning:
                pixelPosition = event.pos #Postion(in pixels) of cursor on board
                # Some clever code that rounds that pixelPosition to match to our Board() objects indexed array
                row = pixelPosition[1] // int(squareSize)
                col = pixelPosition[0] // int(squareSize)
                if game.board.bEmptySquare(row, col): #If space is open
                    game.makeMove(row, col)
                    if bDebug:print(game.board)

                    if board.bGameOver():#Ensures minimax is not called on a finnished game
                        print("Time of moves:")
                        for i in range(len(listOfTimePermoves)):
                            print(f"Move {i+1} time: {listOfTimePermoves[i]} ")
                        game.bGameRunning = False
            if game.currentPlayer == computer.player and game.bGameRunning:
                #Implement minimax algorithm 
                start = time()
                # row, col = computer.bestMove(board)
                row, col = computer.miniMax_AlphaBeta(board,-infinity, infinity)[1]

                stop = time()
                listOfTimePermoves.append(stop-start)
                game.makeMove(row, col)
                
        pygame.display.update() #refreshes everything continuously
main()