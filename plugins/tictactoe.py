import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
import random
import logging

logger = logging.getLogger(__name__)
games = {}

class TicTacToeGame:
    def __init__(self, player_1, player_2, single_player=False):
        self.board = [' '] * 9
        self.players = {player_1: '❌', player_2: '⭕'}
        self.current_player = player_1
        self.single_player = single_player
        self.bot_player = player_2 if single_player else None
        self.game_over = False
        self.winner = None

    def make_move(self, position, player):
        if self.board[position] == ' ' and not self.game_over:
            self.board[position] = self.players[player]
            if self.check_winner():
                self.game_over = True
                self.winner = player
                return f"{self.players[player]} wins!"
            elif ' ' not in self.board:
                self.game_over = True
                return "It's a draw!"
            else:
                self.current_player = self.get_opponent(player)
                return None
        return "Invalid move or game is over!"

    def get_opponent(self, player):
        return [p for p in self.players if p != player][0]

    def check_winner(self):
        b = self.board
        wins = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for w in wins:
            if b[w[0]] == b[w[1]] == b[w[2]] != ' ':
                return True
        return False

    async def bot_move(self):
        if not self.single_player or self.game_over:
            return

        await asyncio.sleep(1)  # Make bot feel more natural

        # First move strategy: take center if free
        if self.board.count(' ') == 9 and self.board[4] == ' ':
            return self.make_move(4, self.bot_player)

        best_score = -float('inf')
        best_move = None

        for i in range(9):
            if self.board[i] == ' ':
                self.board[i] = self.players[self.bot_player]
                score = self.minimax(0, False)
                self.board[i] = ' '
                if score > best_score:
                    best_score = score
                    best_move = i

        if best_move is not None:
            return self.make_move(best_move, self.bot_player)

    def minimax(self, depth, is_maximizing):
        if self.check_winner():
            return -10 + depth if is_maximizing else 10 - depth
        elif ' ' not in self.board:
            return 0

        if is_maximizing:
            max_eval = -float('inf')
            for i in range(9):
                if self.board[i] == ' ':
                    self.board[i] = self.players[self.bot_player]
                    eval = self.minimax(depth + 1, False)
                    self.board[i] = ' '
                    max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            human = self.get_opponent(self.bot_player)
            for i in range(9):
                if self.board[i] == ' ':
                    self.board[i] = self.players[human]
                    eval = self.minimax(depth + 1, True)
                    self.board[i] = ' '
                    min_eval = min(min_eval, eval)
            return min_eval

    def get_board(self):
        b = self.board
        player_names = list(self.players.keys())
        p1, p2 = player_names[0], player_names[1]
        s1, s2 = self.players[p1], self.players[p2]

        p1_display = f"@{p1}" if isinstance(p1, str) and not str(p1).isdigit() else "Player 1"
        p2_display = f"@{p2}" if isinstance(p2, str) and not str(p2).isdigit() else "Player 2"

        current_symbol = self.players[self.current_player]
        current_display = p1_display if self.current_player == p1 else p2_display

        turn_msg = f"\n\n<b>🎯 Turn:</b> {current_symbol} {current_display}"

        board = "<b>🎲 Tic Tac Toe Game!</b>\n🧩 Tap the buttons below to make a move."

        player_info = f"\n\n<b>{p1_display}</b>   {s1}\n<b>{p2_display}</b>   {s2}"

        return board + turn_msg + player_info

# Send board
async def send_game_board(client, message_or_cbq, game_key):
    game = games.get(game_key)
    if not game:
        return
    markup = generate_board_markup(game_key)
    board = game.get_board()

    if isinstance(message_or_cbq, CallbackQuery):
        await message_or_cbq.edit_message_text(board, reply_markup=markup)
    else:
        await message_or_cbq.reply(f"<b>🎮 Tic Tac Toe</b>\n{board}", reply_markup=markup)

# Generate inline board
def generate_board_markup(game_key):
    game = games.get(game_key)
    buttons = []
    for i in range(0, 9, 3):
        row = []
        for j in range(3):
            cell = i + j
            text = game.board[cell] if game.board[cell] != ' ' else '⬜'
            row.append(InlineKeyboardButton(text, callback_data=f"move|{game_key}|{cell}"))
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)

def get_user_id_safe(message_or_cbq):
    """Return a consistent ID for regular or anonymous users."""
    if hasattr(message_or_cbq, "from_user") and message_or_cbq.from_user:
        return message_or_cbq.from_user.id
    if hasattr(message_or_cbq, "sender_chat") and message_or_cbq.sender_chat:
        return f"anon_{message_or_cbq.chat.id}_{message_or_cbq.message_id}"
    return None


@Client.on_message(filters.command("tictactoe"))
async def start_game(client: Client, message: Message):
    user_id = get_user_id_safe(message)
    if not user_id:
        await message.reply("❌ Cannot detect player identity.")
        return

    args = message.command[1:]
    if args and args[0].startswith("@"):
        opponent = args[0].replace("@", "")
        game_key = f"{user_id}-{opponent}"
        games[game_key] = TicTacToeGame(user_id, opponent)
        await message.reply(f"🤝 Multiplayer game started with @{opponent}")
    else:
        bot_id = "BOT"
        game_key = f"{user_id}-bot"
        games[game_key] = TicTacToeGame(user_id, bot_id, single_player=True)
        await send_game_board(client, message, game_key)


@Client.on_callback_query(filters.regex(r"^move\|"))
async def handle_move(client: Client, cbq: CallbackQuery):
    _, game_key, cell = cbq.data.split("|")
    cell = int(cell)
    game = games.get(game_key)

    user_id = get_user_id_safe(cbq)
    if not user_id or not game or game.game_over:
        await cbq.answer("Invalid or finished game.", show_alert=True)
        return

    if user_id != game.current_player:
        await cbq.answer("⛔ Not your turn!", show_alert=True)
        return

    result = game.make_move(cell, user_id)

    if game.single_player and not game.game_over:
        await game.bot_move()

    await send_game_board(client, cbq, game_key)

    if game.game_over:
        result_text = "🤝 It's a draw!" if not game.winner else f"🎉 {game.players[game.winner]} wins!"
        replay_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Replay", callback_data=f"replay|{game_key}")]])
        await cbq.message.reply(f"<b>🎮 Game Over!</b>\n{result_text}", reply_markup=replay_markup)


@Client.on_callback_query(filters.regex(r"^replay\|"))
async def handle_replay(client: Client, cbq: CallbackQuery):
    _, game_key = cbq.data.split("|")
    game = games.get(game_key)
    if not game:
        return

    games[game_key] = TicTacToeGame(*list(game.players.keys()), single_player=game.single_player)
    await send_game_board(client, cbq, game_key)


# Main async entry point for the bot
async def main():
    # Replace 'my_bot' with your actual bot name
    app = Client("my_bot")
    await app.start()

    # Keep the bot running
    await app.idle()

if __name__ == "__main__":
    try:
        asyncio.run(main())  # Ensures the event loop is only run once
    except RuntimeError:
        # Handle case where the event loop is already running
        print("Event loop is already running.")
