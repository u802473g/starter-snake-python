# Group14
# Python 3.12.3

from tabnanny import check
from turtle import distance
import typing
import copy
from enum import Enum

# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#4B89C8",  # TODO: Choose color
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
class GridState(Enum):
    SPACE = 0
    FOOD = -1
    EXPLORED = -2
    MY_HEAD = 1
    MY_BODY = 2
    MY_TAIL = 3
    ENEMY_HEAD = 11
    ENEMY_BODY = 12
    ENEMY_TAIL = 13

class Snake:
    def __init__(self,game_state,snake_id):
        snakes = game_state['board']['snakes']
        if len(snakes) < snake_id:
            return
        self.body = snakes[snake_id]["body"]
        self.length = snakes[snake_id]["length"]
        self.health =  snakes[snake_id]["health"]
        self.head = self.body[0]
        self.neck = self.body[1]
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

        if self.my_snake.length <= self.enemy_snake.length:
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if self.check_range(nx, ny) and self.grid[nx][ny] == GridState.ENEMY_HEAD:
                    return False

        return True   
        
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
    def __init__(self,board,my_snake):
        self.board = board
        self.my_snake = my_snake
        self.grid_copy = copy.deepcopy(board.grid)
        self.grid_copy_fill = None
        self.grid_copy_fill_food = None
        self.food_candidates = []
        self.MAX_DEPTH = 8
        if self.my_snake.length >= 8:
            self.MAX_DEPTH = 9
        if self.my_snake.length >= 15:
            self.MAX_DEPTH = 12
        if self.my_snake.length >= 20:
            self.MAX_DEPTH = 13
        if self.my_snake.length >= 25:
            self.MAX_DEPTH = self.my_snake.length - 12

        self.food_counts = {"up": 3, "down": 3, "left": 3, "right": 3}
        self.explored_counts = {"up": 0, "down": 0, "left": 0, "right": 0}

        self.ALL_SIMULATION_PATHS = []

    def _simulate_all_paths(self,current_x,current_y,depth,path_list,tail_stop,food_count=0):
        if self.is_empty(current_x, current_y, tail_stop) == False or self.grid_copy[current_x][current_y] == GridState.EXPLORED:
            return
        
        if depth >=self.MAX_DEPTH:
            self.ALL_SIMULATION_PATHS.append({
                's':self.my_snake.head,
                'e':{'x':current_x,'y':current_y},
                'd':depth
                })
            return

        tail_index = self.my_snake.length + food_count - depth - 2
        next_tail_cell, current_tail_cell = None, None
        next_tail_x, current_tail_x = None, None
        
        if tail_index >= 0:
            # 既存の_count_reachble_waysからコピーしたロジック
            next_tail_x = self.my_snake.body[tail_index]['x']
            next_tail_y = self.my_snake.body[tail_index]['y']
            current_tail_x = self.my_snake.body[tail_index+1]['x']
            current_tail_y = self.my_snake.body[tail_index+1]['y']
            next_tail_cell = self.grid_copy[next_tail_x][next_tail_y]
            current_tail_cell = self.grid_copy[current_tail_x][current_tail_y]
            
            self.grid_copy[next_tail_x][next_tail_y] = GridState.MY_TAIL
            self.grid_copy[current_tail_x][current_tail_y] = GridState.SPACE

        # 3-2. 現在の頭の位置を占有（探索済みとしてマーク）
        current_cell = self.grid_copy[current_x][current_y]
        self.grid_copy[current_x][current_y] = GridState.EXPLORED # 占有

        # 3-3. 食糧の有無判定と状態の更新
        next_food_count = food_count
        next_tail_stop = tail_stop
        if self.board.grid[current_x][current_y] == GridState.FOOD and food_count == 0:
            next_food_count += 1
            next_tail_stop = True # 食糧を見つけたら、尻尾は動かないシミュレーションへ

        # --- 4. 探索の継続（次の手へ） ---
        if depth < self.MAX_DEPTH:
            for vector in [[1,0], [-1,0], [0,1], [0,-1]]:
                next_x, next_y = current_x + vector[0], current_y + vector[1]
                
                # 次のマスを再帰的に探索
                self._simulate_all_paths(next_x, next_y, depth + 1, path_list, next_tail_stop, next_food_count)

        # --- 5. 盤面状態の復元（バックトラック） ---
        self.grid_copy[current_x][current_y] = current_cell # 占有を解放
        
        if tail_index >= 0:
            # 尻尾の状態を元に戻す
            self.grid_copy[next_tail_x][next_tail_y] = next_tail_cell
            self.grid_copy[current_tail_x][current_tail_y] = current_tail_cell

    def get_food_next_counts(self):
        NEXT_FOOD_POINT = 2
        vectors = {"up": [0,1], "down": [0,-1], "left": [-1,0], "right": [1,0]}
        food_next_counts = {"up": 0, "down": 0, "left": 0, "right": 0}
        my_head_x = self.my_snake.head['x']
        my_head_y = self.my_snake.head['y']
        for move in ["up","down","left","right"]:
            for food in self.board.foods:
                if abs(my_head_x + vectors[move][0] - food['x']) + abs(my_head_y + vectors[move][1] - food['y']) == 1:
                    food_next_counts[move] += NEXT_FOOD_POINT
        return food_next_counts


    def get_direction_counts(self):
        direction_counts = {"up": 0, "down": 0, "left": 0, "right": 0}

        dx = self.my_snake.head['x'] - self.my_snake.neck['x'] 
        dy = self.my_snake.head['y'] - self.my_snake.neck['y']
        i = 1
        for i in range(2,min(self.my_snake.length - 1,6)):
            if self.my_snake.body[i]['x'] != self.my_snake.head['x'] - dx * i or  self.my_snake.body[i]['y'] != self.my_snake.head['y'] - dy * i:
                break

        if dx == 1 and dy == 0:
            direction_counts['right'] = i
        elif dx == -1 and dy == 0:
            direction_counts['left'] = i
        elif dx == 0 and dy == 1:
            direction_counts['up'] = i
        elif dx == 0 and dy == -1:
            direction_counts['down'] = i
        return direction_counts

    def get_safe_moves(self):
        is_move_safe = {"up": True, "down": True, "left": True, "right": True}
        if self.board.is_empty(self.my_snake.head['x'] + 1,self.my_snake.head['y']) == False:
            is_move_safe['right'] = False
        if self.board.is_empty(self.my_snake.head['x'] - 1,self.my_snake.head['y']) == False:
            is_move_safe['left'] = False
        if self.board.is_empty(self.my_snake.head['x'],self.my_snake.head['y'] + 1) == False:
            is_move_safe['up'] = False        
        if self.board.is_empty(self.my_snake.head['x'],self.my_snake.head['y'] - 1) == False:
            is_move_safe['down'] = False
        safe_moves = []
        for move, isSafe in is_move_safe.items():
            if isSafe:
                safe_moves.append(move)
        return safe_moves
    
    def asess_food_counts(self):
        return self.food_counts
    
    def asess_explored_counts(self):
        return self.explored_counts
    
    def get_food_candidates(self):
        return self.food_candidates

    def asess_tail_distances(self):
        tail_distances = {"up": 0, "down": 0, "left": 0, "right": 0}
        vectors = {"up": [0,1], "down": [0,-1], "left": [-1,0], "right": [1,0]}

        my_length = self.my_snake.length
        next_my_tail_x = self.my_snake.body[my_length - 2]['x']
        next_my_tail_y = self.my_snake.body[my_length - 2]['y']
        my_head_x = self.my_snake.head['x']
        my_head_y = self.my_snake.head['y']

        for move in ["up","down","left","right"]:
            distance = abs(my_head_x + vectors[move][0] - next_my_tail_x) + abs(my_head_y + vectors[move][1] - next_my_tail_y)
            if distance == 1:
                if self.my_snake.length >= 25:
                    tail_distances[move] = 0
                else:
                    tail_distances[move] = 2
            else:
                tail_distances[move] = distance - 1
        return tail_distances
    
    def count_explored(self):
        explored_count = 0
        for x in range(self.board.width):
            for y in range(self.board.height):
                if self.grid_copy_fill[x][y] == GridState.EXPLORED:
                    explored_count += 1
        return explored_count
            
    def count_explored_food(self):
        explored_count = 0
        for x in range(self.board.width):
            for y in range(self.board.height):
                if self.grid_copy_fill_food[x][y] == GridState.EXPLORED:
                    explored_count += 1
        return explored_count
    
    def asess_reachble_counts(self):
        reachble_counts = {"up": 0, "down": 0, "left": 0, "right": 0}
        for move in ["up", "down", "left", "right"]:
            current_x,current_y = self.my_snake.head['x'],self.my_snake.head['y']
            next_x,next_y = current_x,current_y
            self.grid_copy_fill = copy.deepcopy(self.board.grid)
            if move == 'up':
                next_y += 1
            elif move == 'down':
                next_y -= 1
            elif move == 'left':
                next_x -= 1
            elif move == 'right':
                next_x += 1
            first_depth = 0
            food_count = 0
            tail_stop = False
            if self.board.is_food(current_x,current_y) == True:
                food_count = 1
                tail_stop = True
                max_depth,total_food_count = self._count_reachble_ways(next_x,next_y,first_depth,move,food_count,tail_stop)
                reachble_counts[move] = max_depth
                self.food_candidates.append({'move':move,'distant':0,'max_depth':max_depth,'food_count':total_food_count,'explored_count':self.count_explored()})          
            else:
                reachble_counts[move],total_food_count = self._count_reachble_ways(next_x,next_y,first_depth,move,food_count,tail_stop)
            self.explored_counts[move] = self.count_explored()
        return reachble_counts

    def _count_reachble_ways(self,current_x,current_y,depth,first_move,food_count,tail_stop):
        if self.is_empty(current_x,current_y,tail_stop) == False or self.grid_copy[current_x][current_y] == GridState.EXPLORED:
            return depth,food_count
        if depth == self.MAX_DEPTH:
            if self.food_counts[first_move] > food_count:
                self.food_counts[first_move] = food_count
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
        self.grid_copy[current_x][current_y] = GridState.EXPLORED
        self.grid_copy_fill[current_x][current_y] = GridState.EXPLORED
        if food_count >= 1:
            self.grid_copy_fill_food[current_x][current_y] = GridState.EXPLORED

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

                if next_tail_stop == True and next_food_count == 1 and total_depth >= self.MAX_DEPTH:  #if self.board.grid[current_x][current_y] == GridState.FOOD:
                    self.food_candidates.append({'move':first_move,'distant':food_distant,'max_depth':total_depth,'food_count':total_food_count,'explored_count':self.count_explored_food() - depth})               
                              
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

# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:
    my_snake = Snake(game_state,0)
    enemy_snake = Snake(game_state,1)
    board = Board(game_state,my_snake,enemy_snake)
    evaluator = Evaluator(board,my_snake)

    next_move = choose_best_move(my_snake,evaluator)

    if next_move == None:
        print(f"MOVE {game_state['turn']}: {next_move}\n")
        return {"move": "down"}
    print(f"MOVE {game_state['turn']}: {next_move}\n")
    return {"move": next_move}



def choose_best_move(my_snake, evaluater):
    # 1. 基本パラメータと安全確認
    HEALTH_LEVEL = max(12, my_snake.length + 5)
    if my_snake.length >= 25:
        HEALTH_LEVEL = my_snake.length + 10
    
    MAX_DEPTH = evaluater.MAX_DEPTH
    safe_moves = evaluater.get_safe_moves()
    
    if not safe_moves:
        print("There is no safe moves!")
        return None

    # 2. 網羅的シミュレーションの実行とフィルタリング
    evaluater.ALL_SIMULATION_PATHS = [] # 収集リストをクリア
    path_metrics = {move: {"variety": 0, "coverage": 0} for move in ["up", "down", "left", "right"]}
    
    for move in safe_moves:
        current_x, current_y = my_snake.head['x'], my_snake.head['y']
        if move == 'up': next_x, next_y = current_x, current_y + 1
        elif move == 'down': next_x, next_y = current_x, current_y - 1
        elif move == 'left': next_x, next_y = current_x - 1, current_y
        elif move == 'right': next_x, next_y = current_x + 1, current_y
        
        # この方向から始まるパスの開始インデックスを記録
        start_idx = len(evaluater.ALL_SIMULATION_PATHS)
        
        # 探索実行
        evaluater._simulate_all_paths(next_x, next_y, 1, [], False, 0)
        
        # この移動方向に関連するパスのみを抽出
        move_paths = evaluater.ALL_SIMULATION_PATHS[start_idx:]
        
        if move_paths:
            # 多様性：MAX_DEPTHまで到達可能な全ルート数
            path_metrics[move]["variety"] = len(move_paths)
            # 広がり：終点のユニーク座標数（エリアの広さ）
            unique_endpoints = {(p['e']['x'], p['e']['y']) for p in move_paths}
            path_metrics[move]["coverage"] = len(unique_endpoints)

    # 3. 補助的な空間・食糧データの取得
    reachble_counts = evaluater.asess_reachble_counts()
    direction_counts = evaluater.get_direction_counts()
    food_counts = evaluater.asess_food_counts()
    explored_counts = evaluater.asess_explored_counts()
    tail_distances = evaluater.asess_tail_distances()
    
    # 重み付け（戦略の設計図）
    VARIETY_W = 1.0    # 選択肢の多さ
    COVERAGE_W = 5.0   # 空間の広がり（重要）
    REACH_W = 10.0     # Flood Fillによる最大到達距離
    FOOD_W = 20.0
    
    move_scores = {move: -9999 for move in ["up", "down", "left", "right"]}

    # 4. 戦略別のスコアリング
    # A. 生存優先戦略 (ヘルス十分)
    if my_snake.health > HEALTH_LEVEL or my_snake.length >= 34:
        for move in safe_moves:
            # 網羅的探索のメトリクスを基本点とする
            sim_score = (path_metrics[move]["variety"] * VARIETY_W) + \
                        (path_metrics[move]["coverage"] * COVERAGE_W)
            
            # 従来の生存指標を統合
            move_scores[move] = sim_score + \
                               (reachble_counts[move] * REACH_W) + \
                               (3 - food_counts[move]) * FOOD_W - \
                               (tail_distances[move] * 1.5) - \
                               (direction_counts[move] * 2.0)
            
    # B. 食糧優先戦略 (ヘルス低下)
    else:
        food_candidates = evaluater.get_food_candidates()
        # 食糧優先時は、シミュレーション結果の中から「食糧を摂った後の生存性」が高いパスを選ぶ
        # ここでは簡易的に、食糧候補の中から「多様性(variety)」が最も高い方向を選択する
        for move in safe_moves:
            sim_score = (path_metrics[move]["variety"] * VARIETY_W) + \
                        (path_metrics[move]["coverage"] * COVERAGE_W)
            
            # 食糧候補リストと照らし合わせる
            is_food_route = any(c['move'] == move for c in food_candidates)
            food_bonus = 50 if is_food_route else 0
            
            move_scores[move] = sim_score + (reachble_counts[move] * REACH_W) + food_bonus

    # 5. 最終決定
    best_move = max(safe_moves, key=lambda m: move_scores[m])
    
    # デバッグ情報の出力（構造の可視化）
    print(f"Metrics: {path_metrics}")
    print(f"Final Scores: {move_scores}")
    
    return best_move

def print_scores(reachble_counts,food_counts,explored_counts,tail_distances,direction_counts,move_scores):
    print(f"reachble count:\n{reachble_counts}")
    print(f"food counts:\n{food_counts}")
    print(f"explored counts:\n{explored_counts}")
    print(f"tail distances:\n{tail_distances}")
    print(f"direction counts:\n{direction_counts}")
    #print(f"food_next_counts:\n{food_next_counts}")
    print(f"move scores:\n{move_scores}")

# Start server when `python main.py` is run
if __name__ == "__main__":
    #os.system('cls')
    from server import run_server
    run_server({"info": info, "start": start, "move": move, "end": end})