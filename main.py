# Group14
# Python 3.12.3

import dis
#from turtle import width
import typing
import copy
from enum import Enum
import os
import math


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#ff7f50",  # TODO: Choose color
        "head": "missile",  # TODO: Choose head
        "tail": "missile",  # TODO: Choose tail
    }

# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")

# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")

# Constant values

MAX_HEALTH = 100
WIDTH = HEIGHT = 11
MAX_DEPTH = 10

class Snake:
    def __init__(self, snake):
        self.id = snake["id"]
        self.name = snake["name"]
        self.body = snake["body"]
        self.length = snake["length"]
        self.health = snake["health"]
        self.head = self.body[0]
        self.neck = self.body[1] if len(self.body) > 1 else None
        self.tail = self.body[-1]
class Board:
    def __init__(self,game_state,my_snake,enemy_snake):
        self.width = game_state['board']['width']
        self.height = game_state['board']['height']
        self.foods = game_state["board"]["food"]
        self.turn = game_state['turn']
        self.grid = [[GridState.SPACE for j in range(self.width)] for i in range(self.height)]
        self.my_snake = my_snake
        self.enemy_snake = enemy_snake
        self.grid_copy = copy.deepcopy(self.grid)
        self._init_grid()

    def _init_grid(self):
        for food in self.foods:
            self.grid[food['x']][food['y']] = GridState.FOOD
        self.grid[self.my_snake.head['x']][self.my_snake.head['y']] = GridState.MY_HEAD
        self.grid[self.my_snake.tail['x']][self.my_snake.tail['y']] = GridState.MY_TAIL
        self.grid[self.enemy_snake.head['x']][self.enemy_snake.head['y']] = GridState.ENEMY_HEAD
        self.grid[self.enemy_snake.tail['x']][self.enemy_snake.tail['y']] = GridState.ENEMY_TAIL
        for i in range(1,self.my_snake.length - 1):
            self.grid[self.my_snake.body[i]['x']][self.my_snake.body[i]['y']] = GridState.MY_BODY

        for i in range(1,self.enemy_snake.length - 1):
            self.grid[self.enemy_snake.body[i]['x']][self.enemy_snake.body[i]['y']] = GridState.ENEMY_BODY

    def is_empty(self, x, y):
        if not self.check_range(x, y):
            return False

        solo_safe = (self.grid[x][y] in [GridState.SPACE, GridState.FOOD] or
                    (self.grid[x][y] == GridState.MY_TAIL and self.my_snake.health < MAX_HEALTH and self.turn > 3))

        if not solo_safe:
            return False
        return True  
    
    def is_headon(self,x,y):
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if self.check_range(nx, ny) and self.grid[nx][ny] == GridState.ENEMY_HEAD:
                if self.my_snake.length <= self.enemy_snake.length:
                    return Result.LOSE
                else:
                    return Result.WIN
        return Result.SAFE
        
    def check_range(self,x,y):
        return x >= 0 and y >= 0 and x < self.width and y < self.height
    
    def is_food(self,x,y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return False
        if self.grid[x][y] == GridState.FOOD:
            return True
        else:
            return False       
    
class Evaluator:
    def __init__(self,board,my_snake,enemy_snake):
        self.board = board
        self.my_snake = my_snake
        self.enemy_snake = enemy_snake
        self.MAX_DEPTH = MAX_DEPTH
        self.grid_copy = copy.deepcopy(board.grid)
        
    def get_safe_moves(self):
        is_empty = {"U": True, "D": True, "L": True, "R": True}
        is_headon = {"U": Result.SAFE, "D": Result.SAFE, "L": Result.SAFE, "R": Result.SAFE}
        is_move_safe = {"U": True, "D": True, "L": True, "R": True}
        my_snake_head_x = self.my_snake.head['x']
        my_snake_head_y = self.my_snake.head['y']
        is_empty['R'] = self.board.is_empty(my_snake_head_x + 1,my_snake_head_y)
        is_empty['L'] = self.board.is_empty(my_snake_head_x - 1,my_snake_head_y)
        is_empty['U'] = self.board.is_empty(my_snake_head_x,my_snake_head_y + 1)    
        is_empty['D'] = self.board.is_empty(my_snake_head_x,my_snake_head_y - 1)
        is_headon["R"] = self.board.is_headon(my_snake_head_x + 1,my_snake_head_y)
        is_headon["L"] = self.board.is_headon(my_snake_head_x - 1,my_snake_head_y)
        is_headon["U"] = self.board.is_headon(my_snake_head_x,my_snake_head_y + 1)
        is_headon["D"] = self.board.is_headon(my_snake_head_x,my_snake_head_y - 1)
        for d in ("U", "D", "L", "R"):
            if is_headon[d] in (Result.WIN,Result.SAFE):
                is_move_safe[d] = is_empty[d]
            else:
                is_move_safe[d] = False
        safe_moves,headon_moves,headon_win_moves = [],[],[]
        for move, isSafe in is_move_safe.items():
            if isSafe:
                safe_moves.append(move)
        for move , isHeadon in is_headon.items():
            if is_empty[move] == True:
                if isHeadon != Result.SAFE:
                    headon_moves.append(move)
                if isHeadon == Result.WIN:
                    headon_win_moves.append(move)
        print(safe_moves,headon_moves,headon_win_moves)
        return safe_moves,headon_moves,headon_win_moves
    
    def asess_reachble_counts(self):
        reachble_counts = {"U": 0, "D": 0, "L": 0, "R": 0}
        for move in ["U", "D", "L", "R"]:
            current_x,current_y = self.my_snake.head['x'],self.my_snake.head['y']
            next_x,next_y = current_x,current_y
            self.grid_copy_fill = copy.deepcopy(self.board.grid)
            if move == 'U':
                next_y += 1
            elif move == 'D':
                next_y -= 1
            elif move == 'L':
                next_x -= 1
            elif move == 'R':
                next_x += 1
            first_depth = 0
            food_count = 0
            tail_stop = False
            if self.board.is_food(current_x,current_y) == True:
                food_count = 1
                tail_stop = True
                max_depth,total_food_count = self._count_reachble_ways(next_x,next_y,first_depth,move,food_count,tail_stop)
                reachble_counts[move] = max_depth
            else:
                reachble_counts[move],total_food_count = self._count_reachble_ways(next_x,next_y,first_depth,move,food_count,tail_stop)
            #self.explored_counts[move] = self.count_explored()
        return reachble_counts

    def _count_reachble_ways(self,current_x,current_y,depth,first_move,food_count,tail_stop):
        if self.is_empty(current_x,current_y,tail_stop) == False or self.grid_copy[current_x][current_y] == GridState.MY_EXPLORED:
            return depth,food_count
        if depth == self.MAX_DEPTH:
            if self.grid_copy[current_x][current_y] != GridState.MY_TAIL:
                return depth + 2,food_count
            else:
                return depth + 1,food_count
            
        max_depth = depth

        tail_index = self.my_snake.length + food_count - depth - 2
        next_tail_x,next_tail_y,current_tail_x,current_tail_y = None,None,None,None

        next_tail_cell,current_tail_cell = None,None
        if tail_index >= 0:
            next_tail_x = self.my_snake.body[tail_index]['x']
            next_tail_y = self.my_snake.body[tail_index]['y']
            current_tail_x = self.my_snake.body[tail_index+1]['x']
            current_tail_y = self.my_snake.body[tail_index+1]['y']
            next_tail_cell = self.grid_copy[next_tail_x][next_tail_y]
            current_tail_cell = self.grid_copy[current_tail_x][current_tail_y]
            self.grid_copy[next_tail_x][next_tail_y] = GridState.MY_TAIL
            self.grid_copy[current_tail_x][current_tail_y] = GridState.SPACE

        current_cell = self.grid_copy[current_x][current_y]
        self.grid_copy[current_x][current_y] = GridState.MY_EXPLORED
        self.grid_copy_fill[current_x][current_y] = GridState.MY_EXPLORED
        if food_count >= 1:
            self.grid_copy_fill_food[current_x][current_y] = GridState.MY_EXPLORED

        past_explored_count = None
        next_food_count = food_count
        next_tail_stop = False
        if self.board.grid[current_x][current_y] == GridState.FOOD:
            food_distant = depth
            next_food_count += 1
            next_tail_stop = True
            if next_food_count == 1:
                self.grid_copy_fill_food = copy.deepcopy(self.grid_copy)

        min_food_count = 3

        if depth < self.MAX_DEPTH:
            for vector in [[1,0],[-1,0],[0,1],[0,-1]]:
                total_depth,total_food_count = self._count_reachble_ways(current_x + vector[0],current_y + vector[1],depth + 1,first_move,next_food_count,next_tail_stop)
                if max_depth < total_depth:
                    max_depth = total_depth
                    min_food_count = total_food_count
                elif  max_depth == total_depth and min_food_count > total_food_count:
                    max_depth = total_depth
                    min_food_count = total_food_count  

                #if next_tail_stop == True and next_food_count == 1 and total_depth >= self.MAX_DEPTH:  #if self.board.grid[current_x][current_y] == GridState.FOOD:
                    #self.food_candidates.append({'move':first_move,'distant':food_distant,'max_depth':total_depth,'food_count':total_food_count,'explored_count':self.count_explored_food() - depth})               
                              
        self.grid_copy[current_x][current_y] = current_cell
        if tail_index >= 0:
            self.grid_copy[next_tail_x][next_tail_y] = next_tail_cell
            self.grid_copy[current_tail_x][current_tail_y] = current_tail_cell
        return max_depth,min_food_count
      
    def is_empty(self,x,y,tail_stop):
        if x < 0 or y < 0 or x >= self.board.width or y >= self.board.height:
            return False
        if self.grid_copy[x][y] == GridState.SPACE or self.grid_copy[x][y] == GridState.FOOD or (self.grid_copy[x][y] == GridState.MY_TAIL and tail_stop == False and self.board.turn > 3):   #empty,food,tail
            return True
        else:
            return False   

    
    def get_stalking_score(self, move):
        """
        相手の「斜め後ろ（死角）」のみを狙うストーキング関数。
        相手の進行方向を計算し、斜め前（衝突コース）を除外する。
        """
        # 1. 自分の次のヘッド位置を計算
        next_my_head_x = self.my_snake.head['x']
        next_my_head_y = self.my_snake.head['y']
        
        if move == "up": next_my_head_y += 1
        elif move == "down": next_my_head_y -= 1
        elif move == "left": next_my_head_x -= 1
        elif move == "right": next_my_head_x += 1

        # 2. 相手の進行方向ベクトルを特定 (Head - Neck)
        enemy_head = self.enemy_snake.head
        enemy_neck = self.enemy_snake.neck
        
        dx = enemy_head['x'] - enemy_neck['x']
        dy = enemy_head['y'] - enemy_neck['y']

        # 3. ターゲット座標の決定（斜め後ろ＝首の隣接マスとする）
        # 進行方向に対して「後ろ」側の斜めのみをリストアップ
        target_candidates = []

        if dx == 1: # 相手は「右」を向いている
            # 斜め後ろは「左上」と「左下」 -> つまり (Head.x - 1, Head.y ± 1)
            target_candidates = [(enemy_head['x'] - 1, enemy_head['y'] + 1), 
                                 (enemy_head['x'] - 1, enemy_head['y'] - 1)]
        elif dx == -1: # 相手は「左」を向いている
            # 斜め後ろは「右上」と「右下」 -> (Head.x + 1, Head.y ± 1)
            target_candidates = [(enemy_head['x'] + 1, enemy_head['y'] + 1), 
                                 (enemy_head['x'] + 1, enemy_head['y'] - 1)]
        elif dy == 1: # 相手は「上」を向いている
            # 斜め後ろは「左下」と「右下」 -> (Head.x ± 1, Head.y - 1)
            target_candidates = [(enemy_head['x'] - 1, enemy_head['y'] - 1), 
                                 (enemy_head['x'] + 1, enemy_head['y'] - 1)]
        elif dy == -1: # 相手は「下」を向いている
            # 斜め後ろは「左上」と「右上」 -> (Head.x ± 1, Head.y + 1)
            target_candidates = [(enemy_head['x'] - 1, enemy_head['y'] + 1), 
                                 (enemy_head['x'] + 1, enemy_head['y'] + 1)]

        # 4. 最短距離の計算
        min_distance = float('inf')

        for tx, ty in target_candidates:
            # マンハッタン距離
            dist = abs(tx - next_my_head_x) + abs(ty - next_my_head_y)
            if dist < min_distance:
                min_distance = dist

        # 距離が近いほど高スコア（ターゲットが遠すぎる場合は評価を下げる）
        # +1 はゼロ除算防止
        return 100.0 / (min_distance + 1)


    
    #ここから追加（最もgood餌を取得する関数）
    def get_best_food(self):
        MY_DISTANCE_W = 4.0
        ENEMY_DISTANCE_W = 2.0
        WALL_DISTANCE_W = 3.0

        #餌の位置を取得
        foods = self.board.foods
        #頭の位置を取得
        my_head = self.my_snake.head
        #aite no hebi no atama
        enemy_head = self.enemy_snake.head

        best_food = None
        #minusの無限大を代入しておく
        max_score = float('-inf')

        board_width = self.board.width
        board_height = self.board.height

        #頭と餌の距離を計算 
        for food in foods:
            my_distance = abs(food['x'] - my_head['x']) + abs(food['y'] - my_head['y'])
            enemy_distance = abs(food['x'] - enemy_head['x']) + abs(food['y'] - enemy_head['y'])

            distance_from_x_wall = min(food['x'], board_width -1 -food['x'])
            distance_from_y_wall = min(food['y'], board_height -1 -food['y'])
            wall_score = distance_from_x_wall + distance_from_y_wall

            score = 0

            score -= my_distance * MY_DISTANCE_W
            score += enemy_distance * ENEMY_DISTANCE_W
            score += wall_score * WALL_DISTANCE_W

            if score > max_score:
                max_score = score
                best_food = food 

        return best_food  
    
    def get_balance_enemy(self):
        x_average = 0
        y_average = 0
        for cell in self.enemy_snake.body:
            x_average += cell['x']
            y_average += cell['y']
        x_average /= self.enemy_snake.length
        y_average /= self.enemy_snake.length
        return x_average,y_average
    
    def get_food_directions(self):
        FOOD_POINT = 1.0
        food_directions = {'U': 0, 'D' : 0, 'L' : 0, 'R' : 0}
        food = self.get_best_food()
        if food == None :
            return food_directions
        if food['x'] > self.my_snake.head['x']:
            food_directions["R"] += FOOD_POINT
        elif food['x'] < self.my_snake.head['x']:
            food_directions["L"] += FOOD_POINT
        if food['y'] > self.my_snake.head['y']:
            food_directions["U"] += FOOD_POINT
        elif food['y'] < self.my_snake.head['y']:
            food_directions["D"] += FOOD_POINT   
        return food_directions
    
    def get_enemy_directions(self):
        ENEMY_POINT = 1.0
        my_head = self.my_snake.head
        enemy_head = self.enemy_snake.head
        distance = abs(my_head['x'] - enemy_head['x']) + abs(my_head['y'] - enemy_head['y'])
        enemy_directions = {'U': 0, 'D' : 0, 'L' : 0, 'R' : 0}
        if enemy_head['x'] > my_head['x']:
            enemy_directions["R"] += ENEMY_POINT
        elif enemy_head['x'] < my_head['x']:
            enemy_directions["L"] += ENEMY_POINT
        if enemy_head['y'] > my_head['y']:
            enemy_directions["U"] += ENEMY_POINT
        elif enemy_head['y'] < my_head['y']:
            enemy_directions["D"] += ENEMY_POINT
        return distance,enemy_directions   

      
class GridState(Enum):
    SPACE = 0
    FOOD = -1
    MY_EXPLORED = 4
    ENEMY_EXPLORED = 5
    MY_HEAD = 1
    MY_BODY = 2
    MY_TAIL = 3
    ENEMY_HEAD = 11
    ENEMY_BODY = 12
    ENEMY_TAIL = 13

class Result(Enum):
    LOSE = -1
    SAFE = 0
    WIN  = 1

DIRS = {
    "U": (0, 1),
    "D": (0, -1),
    "L": (-1, 0),
    "R": (1, 0)
}

STRING_DIRS_CONVERSION = {
    "U": "up",
    "D": "down",
    "L": "left",
    "R": "right"
}

class Stats:
    def __init__(self):
        self.my_move_sum = 0
        self.enemy_move_sum = 0
        self.node_count = 0
        self.safe_count = 0
        self.lose_count = 0
        self.win_count = 0
        self.my_space_danger = 0
        self.enemy_space_danger = 0

class Simulator:
    def __init__(self,board,my_snake,enemy_snake):
        self.board = board
        self.grid = copy.deepcopy(board.grid)
        self.width = board.width
        self.height = board.height
        for x in range(self.width):
            for y in range(self.height):
                if self.grid[x][y] in (GridState.MY_BODY,GridState.MY_HEAD):
                    self.grid[x][y] = GridState.MY_EXPLORED
                if self.grid[x][y] in (GridState.ENEMY_BODY,GridState.ENEMY_HEAD):
                    self.grid[x][y] = GridState.ENEMY_EXPLORED
        self.my_body = copy.deepcopy(my_snake.body)
        self.enemy_body = copy.deepcopy(enemy_snake.body)
        self.my_head = my_snake.head
        self.enemy_head = enemy_snake.head
        self.my_health = my_snake.health
        self.enemy_health = enemy_snake.health
        self.my_tail_stop = False
        self.enemy_tail_stop = False
        self.my_length = my_snake.length
        self.enemy_length = enemy_snake.length
        self.MAX_DEPTH = 5

    def check_range(self,x,y):
        return 0 <= x < self.width and 0 <= y < self.height
    
    def legal_moves(self,x, y,my_tail_stop,enemy_tail_stop):
        moves = []
        for d, (dx, dy) in DIRS.items():
            nx = x + dx
            ny = y + dy
            if self.check_range(nx, ny) and self.is_empty(nx,ny,my_tail_stop,enemy_tail_stop):
                moves.append((d, nx, ny))
        return moves
    
    def get_space_score(self,x,y):
        space_score = 0
        if x in (0,self.width - 1):
            space_score += 5000
        elif x in (1,self.width - 2):
            space_score += 50
        elif x in (2,self.width - 3):
            space_score += 1
        if y in (0,self.width-1):
            space_score += 5000
        elif y in (1,self.width - 2):
            space_score += 500
        elif y in (2,self.width - 3):
            space_score += 1
        return space_score
        
    def dfs(self,depth,my_food_count,enemy_food_count,mx,my,ex,ey,my_tail_stop,enemy_tail_stop):
        if depth == self.MAX_DEPTH:
            self.stats.safe_count += 1
            return        
        my_moves  = self.legal_moves(mx,my,my_tail_stop,enemy_tail_stop)
        enemy_moves = self.legal_moves(ex,ey,my_tail_stop,enemy_tail_stop)

        if len(enemy_moves) == 0:
            self.stats.win_count += 1
            self.stats.safe_count += 1
        if len(my_moves) == 0:
            self.stats.lose_count += 1

        self.stats.my_space_danger += self.get_space_score(mx,my)
        self.stats.enemy_space_danger += self.get_space_score(ex,ey)

        self.stats.my_move_sum  += len(my_moves)
        self.stats.enemy_move_sum += len(enemy_moves)
        self.stats.node_count   += 1

        for _, mnx, mny in my_moves:
            for _, enx, eny in enemy_moves:
                my_dead,enemy_dead = self.judge_death(depth,mnx,mny,enx,eny,my_food_count,enemy_food_count,my_tail_stop,enemy_tail_stop)
                if not my_dead and not enemy_dead:
                    changed,my_ate,enemy_ate,removed_my_tail,removed_enemy_tail = self.apply_move(mnx,mny,enx,eny,my_tail_stop,enemy_tail_stop)
                    if my_ate:
                        my_food_count += 1
                    if enemy_ate:
                        enemy_food_count += 1
                    self.dfs(depth + 1,my_food_count,enemy_food_count,mnx,mny,enx,eny,my_ate,enemy_ate)
                    self.undo(changed,removed_my_tail,removed_enemy_tail)
                elif my_dead == True:
                    self.stats.lose_count += 1
                elif my_dead == False and enemy_dead == True:
                    self.stats.win_count += 1
                    self.stats.safe_count += 1

    def is_empty(self, x, y, my_tail_stop, enemy_tail_stop):
        state = self.grid[x][y]

        if state in (GridState.SPACE, GridState.FOOD):
            return True
        if state == GridState.MY_TAIL:
            return not my_tail_stop
        if state == GridState.ENEMY_TAIL:
            return not enemy_tail_stop
        return False    

    def judge_death(self,depth,mnx,mny,enx,eny,my_food_count,enemy_food_count,my_tail_stop,enemy_tail_stop):
        my_dead  = not (self.check_range(mnx, mny) and self.is_empty(mnx,mny,my_tail_stop,enemy_tail_stop)) or self.my_health - depth + my_food_count*100 < 1
        enemy_dead = not (self.check_range(enx, eny) and self.is_empty(enx,eny,my_tail_stop,enemy_tail_stop)) or self.enemy_health - depth + enemy_food_count*100 < 1

        my_length = len(self.my_body)
        enemy_length = len(self.enemy_body)
        if (mnx, mny) == (enx, eny):
            if my_length >= enemy_length:
                enemy_dead = True
            if my_length <= enemy_length:
                my_dead = True
        return my_dead,enemy_dead

    def apply_move(self,mnx,mny,enx,eny,my_tail_stop,enemy_tail_stop):
        changed = []
        my_ate = (self.grid[mnx][mny] == GridState.FOOD)
        enemy_ate = (self.grid[enx][eny] == GridState.FOOD)

        for x, y in [(mnx, mny), (enx, eny)]:
            changed.append((x, y, self.grid[x][y]))
        
        self.grid[mnx][mny] = GridState.MY_EXPLORED
        self.grid[enx][eny] = GridState.ENEMY_EXPLORED

        self.my_body.insert(0,{"x": mnx, "y": mny})
        self.enemy_body.insert(0,{"x": enx, "y": eny})
        removed_my_tail,removed_enemy_tail = None,None

        if not my_tail_stop:
            removed_my_tail,tx, ty = self.pop_my_tail()
            new_tail = self.my_body[-1]
            ntx,nty = new_tail['x'],new_tail['y']
            changed.append((tx, ty, self.grid[tx][ty]))
            changed.append((ntx,nty,self.grid[ntx][nty]))
            self.grid[tx][ty] = GridState.SPACE
            self.grid[ntx][nty] = GridState.MY_TAIL

        if not enemy_tail_stop:
            removed_enemy_tail,tx, ty = self.pop_enemy_tail()
            new_tail = self.enemy_body[-1]
            ntx,nty = new_tail['x'],new_tail['y']
            changed.append((tx, ty, self.grid[tx][ty]))
            changed.append((ntx,nty,self.grid[ntx][nty]))
            self.grid[tx][ty] = GridState.SPACE
            self.grid[ntx][nty] = GridState.ENEMY_TAIL

        return changed, my_ate, enemy_ate,removed_my_tail,removed_enemy_tail
    
    def undo(self,changed,removed_my_tail,removed_enemy_tail):
        for x, y, old in changed:
            self.grid[x][y] = old
        if removed_my_tail is not None:
            self.my_body.append(removed_my_tail)
        if removed_enemy_tail is not None:
            self.enemy_body.append(removed_enemy_tail)
        self.my_body.pop(0)
        self.enemy_body.pop(0)

    def pop_my_tail(self):
        tail_state = self.my_body.pop()
        return tail_state,tail_state['x'] , tail_state['y']
    
    def pop_enemy_tail(self):
        tail_state = self.enemy_body.pop()
        return tail_state,tail_state['x'] , tail_state['y']

    def evaluate_first_moves(self):
        result = {}
        depth = 0
        mx,my = self.my_head['x'],self.my_head['y']
        ex,ey = self.enemy_head['x'],self.enemy_head['y']
        my_food_count = 0
        enemy_food_count = 0
        my_tail_stop,enemy_tail_stop = False,False
        if self.my_health == MAX_HEALTH:
            my_food_count += 1
            my_tail_stop = True
        if self.enemy_health == MAX_HEALTH:
            enemy_food_count += 1
            enemy_tail_stop = True
        
        my_moves = self.legal_moves(mx,my,my_tail_stop,enemy_tail_stop)
        enemy_moves = self.legal_moves(ex,ey,my_tail_stop,enemy_tail_stop)

        for d, mnx, mny in my_moves:
            self.stats = Stats()
            self.stats.node_count   += 1
            if len(enemy_moves) == 0:
                self.stats.win_count += 1
                self.stats.safe_count += 1
            if len(my_moves) == 0:
                self.stats.lose_count += 1
            self.stats.my_space_danger += self.get_space_score(mx,my)
            self.stats.enemy_space_danger += self.get_space_score(ex,ey)
            for _, enx, eny in enemy_moves:
                my_dead,enemy_dead = self.judge_death(depth,mnx,mny,enx,eny,my_food_count,enemy_food_count,my_tail_stop,enemy_tail_stop)
                if not my_dead and not enemy_dead:
                    changed,my_ate,enemy_ate,removed_my_tail,removed_enemy_tail = self.apply_move(mnx,mny,enx,eny,my_tail_stop,enemy_tail_stop)
                    if my_ate:
                        my_food_count += 1
                    if enemy_ate:
                        enemy_food_count += 1
                    self.dfs(depth + 1,my_food_count,enemy_food_count,mnx,mny,enx,eny,my_ate,enemy_ate)
                    self.undo(changed,removed_my_tail,removed_enemy_tail)
                elif my_dead == True:
                    self.stats.lose_count += 1
                elif my_dead == False and enemy_dead == True:
                    self.stats.win_count += 1
                    self.stats.safe_count += 1
            result[d] = copy.copy(self.stats)
        return result

# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    board_snakes = game_state["board"]["snakes"]

    if len(board_snakes) < 2:
        return {"move": "down"}

    my_snake = Snake(game_state["you"])

    enemy_raw = next(
        snake for snake in board_snakes
        if snake["id"] != game_state["you"]["id"]
    )
    enemy_snake = Snake(enemy_raw)

    board = Board(game_state,my_snake,enemy_snake)
    evaluator = Evaluator(board,my_snake,enemy_snake)
    simulator = Simulator(board,my_snake,enemy_snake)

    next_move = choose_best_move(board,my_snake,enemy_snake,evaluator,simulator)

    if next_move == None:
        print(f"MOVE {game_state['turn']}: {next_move}\n")
        return {"move": "right"}
    print(f"MOVE {game_state['turn']}: {next_move}\n")
    return {"move": next_move}

def choose_best_move(board, my_snake, enemy_snake, evaluater, simulator):
    INF = 10**12
    W_SAFE = 1.0
    W_WIN  = 2.0
    W_LOSE = 5.0
    W_NODE = 1.0
    W_SPACE = 1.0
    W_DANGER = 2.0
    STALKING_W = 5.0
    FOOD_W = 0
    HEALTH_LEBEL = 20
    DISTANCE_LEVEL = 5
    
    W_WALL_KILL    = 50000.0  # 斜め前
    W_WALL_STALK   = 40000.0  # 斜め後ろ
    W_BLOCK_PATH   = 100000.0 # 強制ルート封鎖
    W_PARALLEL     = 20000.0  # ▼ 追加: 並走
    W_2PARALLEL    = 1500.0
    
    length_diff = my_snake.length - enemy_snake.length
    distance, enemy_directions = evaluater.get_enemy_directions()

    if length_diff >= 3:
        if my_snake.health > HEALTH_LEBEL:
            FOOD_W = 0
            STALKING_W = 100
        else:
            FOOD_W = 100 * (MAX_HEALTH - my_snake.health)
    elif length_diff > 0:
        FOOD_W = 100 * (MAX_HEALTH - my_snake.health)
    else:
        if distance >= DISTANCE_LEVEL:
            FOOD_W = 100 * (MAX_HEALTH - my_snake.health - length_diff)
        else:
            STALKING_W = -100
    if board.turn <= 60:
        FOOD_W = 5000

    safe_moves, headon_moves, headon_win_moves = evaluater.get_safe_moves()
    reachble_counts = evaluater.asess_reachble_counts()
    food_directions = evaluater.get_food_directions()
    result = simulator.evaluate_first_moves()

    #敵の状況
    ex, ey = enemy_snake.head['x'], enemy_snake.head['y']
    edx, edy = 0, 0
    if enemy_snake.neck:
        enx, eny = enemy_snake.neck['x'], enemy_snake.neck['y']
        edx, edy = ex - enx, ey - eny 

    is_enemy_at_wall = (ex == 0 or ex == board.width - 1 or ey == 0 or ey == board.height - 1)

    diag_candidates = []   
    stalk_candidates = []  
    forced_target = None

    if edx != 0 or edy != 0:
        #斜め前の座標計算
        c1_front = (ex + edx + edy, ey + edy - edx) 
        c2_front = (ex + edx - edy, ey + edy + edx) 
        diag_candidates = [c1_front, c2_front]

        #斜め後ろの座標計算
        c1_back = (ex - edx + edy, ey - edy - edx) 
        c2_back = (ex - edx - edy, ey - edy + edx) 
        stalk_candidates = [c1_back, c2_back]

        #敵の前方、左、右の座標計算
        front_x, front_y = ex + edx, ey + edy
        side1_x, side1_y = ex - edy, ey + edx
        side2_x, side2_y = ex + edy, ey - edx

        #前が開いているか、左右がふさがれているか
        is_front_open = board.check_range(front_x, front_y) and board.is_empty(front_x, front_y)
        is_side1_blocked = not (board.check_range(side1_x, side1_y) and board.is_empty(side1_x, side1_y))
        is_side2_blocked = not (board.check_range(side2_x, side2_y) and board.is_empty(side2_x, side2_y))

        #前が開いていて、左右が塞がれているならば、1つ前のマスに必ず行く
        if is_front_open and is_side1_blocked and is_side2_blocked:
            forced_target = (front_x, front_y)

    scores = {}

    for d, s in result.items():
        scores[d] = 0.0
        LOSE_W = 1.0
        
        if s.safe_count == 0 or reachble_counts[d] < MAX_DEPTH:
            scores[d] = -INF
            LOSE_W = 0
            continue

        if d in headon_moves:
            if d not in headon_win_moves:
                scores[d] = -INF // 2
                LOSE_W = 0
                continue
            elif s.lose_count == 0:
                scores[d] = INF
                continue

        mx, my = my_snake.head['x'], my_snake.head['y']
        if d == "U": my += 1
        elif d == "D": my -= 1
        elif d == "L": mx -= 1
        elif d == "R": mx += 1

        # --- 基本スコア計算 ---
        node = max(1, s.node_count)

        safe_rate = safe_div(s.safe_count, node)
        win_rate  = safe_div(s.win_count, node)
        lose_rate = safe_div(s.lose_count, node)

        survival_score = (
            W_SAFE * safe_rate
            + W_WIN  * win_rate
            - W_LOSE * lose_rate
            + W_NODE * math.log(node)
        )

        # 空間評価
        my_space   = safe_div(s.my_move_sum, node)
        enemy_space = safe_div(s.enemy_move_sum, node)
        space_score = my_space - enemy_space

        # 危険度
        my_danger   = safe_div(s.my_space_danger, node)
        enemy_danger = safe_div(s.enemy_space_danger, node)
        danger_score = enemy_danger - my_danger

        food_score = food_directions.get(d, 0)

        stalking_score = enemy_directions.get(d,0)

        # 合成
        scores[d] += (
            survival_score
            + W_SPACE * space_score
            + W_DANGER * danger_score
            + FOOD_W * food_score
            + STALKING_W * stalking_score * LOSE_W
        )

        # ---- debug ----
        print(f"[{d}]")
        print(" survival:", survival_score)
        print(" space:", space_score)
        print(" danger:", danger_score)
        print(" food:", food_score)
        print(" stalking:", stalking_score)
        # --- ボーナス加算 ---

        # 1. 壁際ボーナス
        if is_enemy_at_wall:
            # 斜め前
            if (mx, my) in diag_candidates:
                scores[d] += W_WALL_KILL
                scores[d] += 10000.0
                print("use diag!!!")

            # 斜め後ろ
            elif (mx, my) in stalk_candidates:
                if length_diff > 0: scores[d] += W_WALL_STALK
                print("use stalk!!!")
            

            # 並走
            # 敵が壁にいて、自分がその1つ内側にいるとき、敵と同じ方向に進む
            else:
                is_parallel = False
                is_2parallel = False
                # 敵が上の壁で左に進んでいる時、自分も左に進む
                if ey == board.height - 1 and my == board.height - 2 and edx == -1 and d == "L": is_parallel = True
                # 敵が上の壁で右に進んでいる時、自分も右
                elif ey == board.height - 1 and my == board.height - 2 and edx == 1 and d == "R": is_parallel = True
                
                # 下の壁
                elif ey == 0 and my == 1 and edx == -1 and d == "L": is_parallel = True
                elif ey == 0 and my == 1 and edx == 1 and d == "R": is_parallel = True
                
                # 左の壁
                elif ex == 0 and mx == 1 and edy == 1 and d == "U": is_parallel = True
                elif ex == 0 and mx == 1 and edy == -1 and d == "D": is_parallel = True
                
                # 右の壁
                elif ex == board.width - 1 and mx == board.width - 2 and edy == 1 and d == "U": is_parallel = True
                elif ex == board.width - 1 and mx == board.width - 2 and edy == -1 and d == "D": is_parallel = True

                # 上の壁 2masu
                elif ey == board.height - 1 and my == board.height - 3 and edx == -1 and d == "L": is_2parallel = True
                elif ey == board.height - 1 and my == board.height - 2 and edx == 1 and d == "R": is_2parallel = True
                
                # 下の壁
                elif ey == 0 and my == 2 and edx == -1 and d == "L": is_2parallel = True
                elif ey == 0 and my == 2 and edx == 1 and d == "R": is_2parallel = True
                
                # 左の壁
                elif ex == 0 and mx == 2 and edy == 1 and d == "U": is_2parallel = True
                elif ex == 0 and mx == 2 and edy == -1 and d == "D": is_2parallel = True
                
                # 右の壁
                elif ex == board.width - 1 and mx == board.width - 3 and edy == 1 and d == "U": is_2parallel = True
                elif ex == board.width - 1 and mx == board.width - 3 and edy == -1 and d == "D": is_2parallel = True
                
                if is_parallel:
                    scores[d] += W_PARALLEL
                    print("use 1parallel!!!")
                elif is_2parallel:
                    scores[d] += W_2PARALLEL
                    print("use 2parallel!!!")

        # 2. 強制ルート封鎖
        if forced_target:
            # forced_target の「進行方向側の1つ先」の座標を計算
            block_x = forced_target[0] + edx
            block_y = forced_target[1] + edy
            
            #移動先が一致
            if (mx, my) == (block_x, block_y):
                scores[d] += W_BLOCK_PATH
                print("number2!!!")

    if scores:
        best_move = max(scores, key=scores.get)

        if scores[best_move] < -INF // 4:
            return STRING_DIRS_CONVERSION[best_move]

        for d in scores:
            s = result[d]
            print(
                d, scores[d],
                "safe", s.safe_count,
                "win", s.win_count,
                "lose", s.lose_count,
                "max_depth",reachble_counts[d]
            )

        return STRING_DIRS_CONVERSION[best_move]
    if safe_moves:
        return STRING_DIRS_CONVERSION[safe_moves[-1]]
    return STRING_DIRS_CONVERSION["R"]


def safe_div(x, y):
    return x / y if y > 0 else 0.0


# Start server when `python main.py` is run
if __name__ == "__main__":
    os.system('cls')
    from server import run_server
    run_server({"info": info, "start": start, "move": move, "end": end})