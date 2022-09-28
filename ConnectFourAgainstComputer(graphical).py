"""
ConnectFourAgainstComputer(graphical).py

A program implementing the minimax recurssive algorithm with alpha beta pruning
and a 'depth' parameter in a connect-4 setting. 


NOTE: I coded all of the code setting up the game and win conditions myself altering 
from my "TickTackToeAgainstComputer(graphical).py" which is what I worked on first.
The Alpha-Beta and functions used to score the board were intergrated from 
https://github.com/KeithGalli/Connect4-Python which is also cited in my papers reference section.


This algorithm is structured very similarly to the tick-tack-toe algorithim.
The only differences are the 'depth', 'alpha', and 'beta' variables which I will
explain in my paper.

Because of the current structure of the code the program cannot calculate every turn
and all associated relevant boards, EVEN with alpha beta pruning. NOTE: There are
ways to do this but they involve using bitboards and a memoization cache (Which I will
explain in my paper).

The algorithim is encouraged to create connections by the following rational.
I have it trying to achieve the highest score, or 'maximizing'.

It is awarded a score of 100 for a 4-in-a-row, a 4 for a 3-aligned, a 2 for 2-aligned,
and a -6 for an opponents 4-in-a-row.

These numbers are not fine tuned but generally seem to work.

As I experimented with the game and playing against it I noticed a similar theme to the 
tik-tack-toe where the the algorithm would sometimes delay its immediate win. But I also
saw that if the algorithim 'knew' it was destined to lose it would end the game early,
so quite plainly the opposite of the quality I describe in the tick-tack-toe program.

GAMEPLAY INSTRUCTIONS:

-The player will always go first

-left click any column to 'drop' a chip.

-if you cannot drop a chip anymore the game has ended
 and a player has won.

-be patient for the algorithim to process in the
 early moves if the depth is set to a 'high' amount.

Finn Thistle | May 2022
"""
import sys
import pygame
import copy
import math
from time import time

# CONSTANT VARIABLES:

    #Board Constants:
width = 900
height = 900
rows = 6
columns = 7
squareSize = width/columns
lineWidth = 10
bgColor = "gray"
lineColor = "blue"
margin = 0
chipRadius = 60
chipWidth = 60
redChip = 1 #human
yellowChip = 2 #computer

    #Other Constants:
infinity = math.inf
screen = pygame.display.set_mode((width, height))
bDebug = True

class Board():
    def __init__(self):
        self.board = [[0 for c in range(columns)] for r in range(rows)]
        self.totalBoardChips = 0
    def __str__(self):
        """Prints the board into terminal."""
        returnString = ""
        for i in range(rows):
            returnString += f"{self.board[i]} \n"
        return returnString
    
    def dropChip(self, column, playerChip): #NOTE: with current return statement this is ONLY meant to be used in the dropChipGraphic()
        """Code that simulates how chips would be dropped in game."""
        for i in range(rows-1, -1, -1):
            if not self.board[i][column]: #if it is empty
                self.board[i][column] = playerChip #drops the chip to the 'bottom most' part of the board
                self.totalBoardChips+=1
                return i, column

    def bBoardFull(self):
        """Returns True if every slot has a chip"""
        return self.totalBoardChips==42
    
    def bColumnFull(self, column):
        """A function returning True if the inputed column is full"""
        return self.board[0][column] !=0

    def columnOpenSlot(self, column):
        """Returns the row position of the next immediate space in a column"""
        for row in range(rows-1, -1, -1):
            if not self.board[row][column]:
                return row
        
    
    def checkBoard(self):
        """
            will return 0 if game is not over
            will return 1 if player 1 wins
            will return 2 if player 2 wins
        """
        #VERTICLE WINS
        for col in range(columns):
            if (self.board[0][col]==self.board[1][col]==self.board[2][col]==self.board[3][col] != 0 or
            self.board[1][col]==self.board[2][col]==self.board[3][col]==self.board[4][col] != 0 or
            self.board[2][col]==self.board[3][col]==self.board[4][col]==self.board[5][col] != 0):
                return self.board[2][col] #Return who occupies that space
        #HORIZONTAL WINS
        for row in range(rows):
            if (self.board[row][0]==self.board[row][1]==self.board[row][2]==self.board[row][3]!=0 or
            self.board[row][1]==self.board[row][2]==self.board[row][3]==self.board[row][4]!=0 or
            self.board[row][2]==self.board[row][3]==self.board[row][4]==self.board[row][5]!=0 or
            self.board[row][3]==self.board[row][4]==self.board[row][5]==self.board[row][6]!=0
            ):
                return self.board[row][3]
        #DIAGNOL WINS
        #NOTE: referenced from https://github.com/KeithGalli/Connect4-Python
        for col in range(columns-3): 
            for row in range(rows-3):#Checks Diagnols increasing
                if self.board[row][col]==self.board[row+1][col+1]==self.board[row+2][col+2]==self.board[row+3][col+3] != 0:
                    return self.board[row][col]
            for r in range(3, rows):#Checks Diagnols decreasing
                if self.board[r][col]==self.board[r-1][col+1]==self.board[r-2][col+2]==self.board[r-3][col+3] != 0:
                    return self.board[r][col]
            
        return 0 #Return 0 if no wins yet
    
    def scoreWindow(self,player, window):#NOTE: referenced from https://github.com/KeithGalli/Connect4-Python
        """
        Scores current window based on how many yellow and
        red chips are counted.
        """
        score = 0
        opponent = redChip
        if player == redChip: 
            opponent = yellowChip
        if window.count(player) == 4:
            score += 100
        elif window.count(player) == 3:          
            score += 4
        elif window.count(player) == 2:
            score += 2

        if window.count(opponent) == 3:  
            score -= 6

        return score
    def scoreOfBoardPosition(self, player):#NOTE: referenced from https://github.com/KeithGalli/Connect4-Python
        """
        Returns a score for the current board as a whole and position
        of chips to influence algorithims column choice.
        """
        score = 0
        # score center column, 
        # gives an incentive to drop chips in the middle because 
        # the more chips in the middle column contains the most possible different
        # connections
        
        centerList = [i for i in self.board[3]] # list of chips in center column
        centerCount = centerList.count(player)
        score += centerCount * 7  #og was 3

        # horizontal
        for row in range(rows):
            rowList = [i for i in self.board[row]]
            for col in range(columns-3):
                window = rowList[col:col+4]
                score += self.scoreWindow(player,window)

        # vertical
        for col in range(columns):
            colList = [i for i in self.board[:col]]
            for row in range(rows-3):
                window = colList[row:row+4]
                score += self.scoreWindow(player,window)

        # diagonal
        for row in range(rows-3):
            for col in range(columns-3):
                window = [self.board[row+i][col+i] for i in range(4)]
                score += self.scoreWindow(player,window)
        for row in range(rows-3):
            for col in range(columns-3):
                window = [self.board[row+3-i][col+i] for i in range(4)]
                score += self.scoreWindow(player,window)

        return score

    def allOpenColumns(self):
        """Returns a list of the remaining open columns"""
        #NOTE: sometimes when there is a single column left open this function will return an empty list
        # this results in an index error on lines 183 and 199 where 'bestMoveYet = openColumnList[0]'
        # I think this may be do to the fact that the algorithim is simulating moves when the board is full
        # so the function returns nothing.
        openColumns = []
        for i in range(columns):
            if not self.bColumnFull(i):
                openColumns.append(i)

        return openColumns
class BestmoveAlgorithm():
    def __init__(self):
        self.player = 2

    def minimax(self, board, depth, maximizingPlayer):
        """An implementation of the min max algorithim with alpa-beta pruning. 
        Using all dynamic variables in its recursive calls."""
        openColumnList = board.allOpenColumns()

        if not openColumnList:return (None, board.scoreOfBoardPosition(yellowChip)) #This is my attempt to fix the problem in my note in the allOpenColumns method above

        case = board.checkBoard()
        if depth == 0 or case:
            if case:
                if case == 2:
                    return (None, infinity)
                elif case == 1:
                    return (None, -infinity)
                else: # board is full at this point
                    return (None, 0)
            else: #depth is 0
                return (None, board.scoreOfBoardPosition(yellowChip))
                # if maximizingPlayer:
                #     return (None, board.scoreOfBoardPosition(yellowChip)) # Score the current board iteration
                # else:
                #     return (None, board.scoreOfBoardPosition(redChip))
        if maximizingPlayer: # Minimizing player(COMPUTER)
            bestScoreYet = -infinity
            bestMoveYet = openColumnList[0] #Initializing it to the first column in the array, which will be changed if a better column is found
            for col in openColumnList:
                tempBoard = copy.deepcopy(board) #create a copy of the current board parameter passed in
                tempBoard.dropChip(col, yellowChip) #simulate dropping a chip here
                tempScore = self.minimax(tempBoard, depth-1, False)[1] #subtracts the recursive depth variable so we can keep track of how many itterations we are going through
                if tempScore > bestScoreYet: #if a better option is found reset the score and the column
                    bestScoreYet = tempScore
                    bestMoveYet = col
            return bestMoveYet, bestScoreYet

        else: # Minimizing player(HUMAN)
            worstScoreYet = infinity
            bestMoveYet = openColumnList[0]
            for col in openColumnList:
                tempBoard = copy.deepcopy(board)
                tempBoard.dropChip(col, redChip)
                tempScore = self.minimax(tempBoard, depth-1, True)[1]
                if tempScore < worstScoreYet:
                    worstScoreYet = tempScore
                    bestMoveYet = col
            return bestMoveYet, worstScoreYet

    def miniMax_AlphaBeta(self, board, depth, alpha, beta, maximizingPlayer):#NOTE: referenced from https://github.com/KeithGalli/Connect4-Python
        """An implementation of the min max algorithim with alpa-beta pruning. 
        Using all dynamic variables in its recursive calls."""
        
        openColumnList = board.allOpenColumns()

        if not openColumnList:return (None, board.scoreOfBoardPosition(yellowChip)) #This is my attempt to fix the problem in my note in the allOpenColumns method above

        case = board.checkBoard()
        if depth == 0 or case:
            if case:
                if case == 2:
                    return (None, infinity)
                elif case == 1:
                    return (None, -infinity)
                else: # board is full at this point
                    return (None, 0)
            else: #depth is 0
                return (None, board.scoreOfBoardPosition(yellowChip))
                # if maximizingPlayer:
                #     return (None, board.scoreOfBoardPosition(yellowChip)) # Score the current board iteration
                # else:
                #     return (None, board.scoreOfBoardPosition(redChip))
        if maximizingPlayer: # Minimizing player(COMPUTER)
            bestScoreYet = -infinity
            bestMoveYet = openColumnList[0] #Initializing it to the first column in the array, which will be changed if a better column is found
            for col in openColumnList:
                tempBoard = copy.deepcopy(board) #create a copy of the current board parameter passed in
                tempBoard.dropChip(col, yellowChip) #simulate dropping a chip here
                tempScore = self.miniMax_AlphaBeta(tempBoard, depth-1, alpha, beta, False)[1] #subtracts the recursive depth variable so we can keep track of how many itterations we are going through
                if tempScore > bestScoreYet: #if a better option is found reset the score and the column
                    bestScoreYet = tempScore
                    bestMoveYet = col
                if bestScoreYet > alpha:   #keep track of alpha value for later iterations of minimax function, and reset it if aplicable
                    alpha = bestScoreYet
                if alpha >= beta: # 'Prune' the tree (Breakout of the loop), as the best response to each of these  options have already been found
                    break
            return bestMoveYet, bestScoreYet

        else: # Minimizing player(HUMAN)
            worstScoreYet = infinity
            bestMoveYet = openColumnList[0]
            for col in openColumnList:
                tempBoard = copy.deepcopy(board)
                tempBoard.dropChip(col, redChip)
                tempScore = self.miniMax_AlphaBeta(tempBoard, depth-1, alpha, beta, True)[1]
                if tempScore < worstScoreYet:
                    worstScoreYet = tempScore
                    bestMoveYet = col
                if worstScoreYet < beta:
                    beta = worstScoreYet
                
                if alpha >= beta: 
                    break
            return bestMoveYet, worstScoreYet
            
    def bestMove(self, board, depth): 
        """Returns a relativly good (but not ENTIRELY optimal) column to place the chip."""
        # Description of parameters for minimax:
        #  the board,
        #  highest depth value I can give within reasonable time,
        #  worst case initial alpha variable,
        #  worst case initial beta variable,
        #  The player calling this function is maximising
        start = time()
        column, payoff = self.miniMax_AlphaBeta(board, depth, -infinity, infinity, True)
        stop = time()
        if bDebug: print(f"Time of depth {depth}: {stop-start}")
        if bDebug: print("Computer chose column", column, "with a payoff of:", payoff)
        return column
class Game():
    def __init__(self):
        self.board = Board()
        self.computer = BestmoveAlgorithm()
        self.drawLines()
        self.currentPlayer=redChip

    def drawLines(self):
        """Draws rows and columns for Connect-4 board"""
        #Pygame startup
        pygame.init()
        screen.fill(bgColor)

        pygame.draw.line(screen, "black", (0, 0), (width, 0), int(squareSize)*2)
        #verticle lines
        for i in range(columns+1):
            pygame.draw.line(screen, lineColor, (squareSize*i, 0), (squareSize*i, height), lineWidth)
        # horizontal lines
        for i in range(rows+1):
            pygame.draw.line(screen, lineColor, (0, height-squareSize*i), (width, height-squareSize*i), lineWidth)
        
    
    def dropChipGraphic(self, col):
        """Marks the square with the designated symobol in the pygame window"""
        # Some clever code that figures out the position of the symbol on the graphical board based off of col and row
        row, column = self.board.dropChip(col, self.currentPlayer)

        chipColor = "yellow"
        if self.currentPlayer==redChip: 
            chipColor = "red"
        center = ( (column * squareSize) + (squareSize //2) , (row * squareSize) + (squareSize //2) + squareSize )
        pygame.draw.circle(screen, chipColor, center, chipRadius, chipWidth)
    
    def nextPlayerTurn(self):
        """Osolates between value one and two"""
        self.currentPlayer = self.currentPlayer % 2 + 1

    def makeMove(self, col):
        """Simulates an entie player move"""
        self.dropChipGraphic(col)
        self.nextPlayerTurn()
def main():
    depthForTimeComplexityTesting = 7 # for timing
    listOfTimePermoves = [] # for timing
    game = Game()
    board = game.board
    computer = game.computer
    bGameOver = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not bGameOver:
                pixelPosition = event.pos #Postion(in pixels) of cursor on board
                # Some clever code that rounds that pixelPosition to match to our Board() objects indexed array
                 #NOTE: minClickHeight?
                col = pixelPosition[0] // int(squareSize)

                if not board.bColumnFull(col):
                    game.makeMove(col)
                else:
                    print("ERROR:SELECTED COLOMN IS FULL.")  
                    print("Open Column indexs:", board.allOpenColumns()) 
        if board.checkBoard() and not bGameOver:
            bGameOver = True
            winner = "Yellow"
            if game.currentPlayer == yellowChip:
                winner = "Red"

            print("Time of moves:")
            for i in range(len(listOfTimePermoves)):
                print(f"Move {i+1} time: {listOfTimePermoves[i]} ")

            print("Game is over!", winner, "has won!")
        if game.currentPlayer==computer.player and not bGameOver:
            #Implement minimax algorithm 

                
                start = time()
                #col = computer.minimax(board, depthForTimeComplexityTesting, True)[0]
                col = computer.bestMove(board, 7)
                stop = time()
                print(f"Time of depth {depthForTimeComplexityTesting}: {stop-start}")
                listOfTimePermoves.append(stop-start)
                game.makeMove(col)
        pygame.display.update()
main()

