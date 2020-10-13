import argparse
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from datetime import datetime
import telegram
import json


class MemeGodBot:

    def __init__(self, api_token, elections):
        self.token = api_token
        self.updater = Updater(token=self.token, use_context=True, request_kwargs={'read_timeout': 10})
        self.election_file = elections
        self.elections = self.read_elections()
        now = datetime.now()
        print("Hello, it's {}".format(now.strftime('%Y%m%d %HH:%MM')))

    def is_election_running(self):
        now = datetime.now()
        if now.weekday() is 0 and now.hour < 23:
            return True
        return False

    def message_received(self, update, context):
        if not self.is_election_running():
            return
        chat_id = str(update.message.chat_id)
        from_user = update.message.from_user
        if not chat_id in self.elections:
            self.elections[chat_id] = {}
        current_election = self.current_election()
        if not current_election in self.elections[chat_id]:
            self.elections[chat_id][current_election] = {"candidates": {}, "votes":{}}
        user_id = str(from_user.id)
        name = from_user.name
        if user_id in self.elections[chat_id][current_election]["candidates"]:
            return
        bot = self.updater.bot
        vote_button = telegram.InlineKeyboardButton(
                text="Vote for {0}".format(name),
                callback_data=json.dumps({"candidate": user_id, "election_date": current_election})
        )
        bot.send_message(chat_id,
                "Soll {0} Meme Gott werden?".format(name),
                reply_markup=telegram.InlineKeyboardMarkup([[vote_button]]))
        self.elections[chat_id][current_election]["candidates"][user_id] = {"name": name, "message": update.message.message_id}
        self.save_elections()

    def start_listening(self):
        message_handler = MessageHandler(Filters.photo, self.message_received)
        callback_handler = CallbackQueryHandler(self.handle_btn_press)
        self.updater.dispatcher.add_handler(message_handler)
        self.updater.dispatcher.add_handler(callback_handler)
        self.updater.start_polling()

    def handle_btn_press(self, update, callback):
        if not self.is_election_running():
            update.callback_query.answer(text="Sorry, die Wahl ist schon vorbei")
        query_data = json.loads(update.callback_query.data)
        chat_id = str(update.callback_query.message.chat.id)
        vote_for = query_data['candidate']
        election_date = query_data['election_date']
        voter = str(update.callback_query.from_user.id)
        self.elections[chat_id][election_date]["votes"][voter] = vote_for
        self.save_elections()
        vote_for_name = self.elections[chat_id][election_date]["candidates"][vote_for]["name"]
        update.callback_query.answer(text="Du hast für {0} gestimmt".format(vote_for_name))

    def call_winner(self, chat_id):
        if chat_id not in self.elections:
            print("No chat with the id {0}".format(chat_id))
            return
        current_election = self.current_election()
        if current_election not in self.elections[chat_id]:
            print("No Election running")
            return
        votes = self.elections[chat_id][current_election]['votes']
        candidates = {}
        for voter in votes:
            candidate = votes[voter]
            if candidate not in candidates:
                candidates[candidate] = 1
            else:
                candidates[candidate] += 1
        result = "Hier die Abstimmungsergebnisse zum dieswöchigen Memegott:\n\n"
        winners = []
        highest_votes = None
        for candidate, votes in sorted(candidates.items(), key=lambda item: item[1], reverse=True):
            result += "{0} - {1}\n".format(self.elections[chat_id][current_election]["candidates"][candidate]["name"], votes)
            if highest_votes is None:
                highest_votes = votes
            if votes == highest_votes:
                winners.append(self.elections[chat_id][current_election]["candidates"][candidate]["message"])
        self.updater.bot.send_message(chat_id, result)
        for message in winners:
            self.updater.bot.send_message(chat_id, reply_to_message_id=message, text="#gewinnermeme")



    def save_elections(self):
        self.election_file.seek(0)
        self.election_file.write(json.dumps(self.elections, indent=4))
        self.election_file.flush()

    def read_elections(self):
        self.election_file.seek(0)
        return json.loads(self.election_file.read())

    def current_election(self):
        now = datetime.now()
        return now.strftime('%Y%m%d')



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', action='store_true')
    parser.add_argument('elections', type=argparse.FileType('r+'))
    parser.add_argument('api_token')
    parser.add_argument('--call-winner', action='store_true')
    parser.add_argument('--chat-id')
    args = parser.parse_args()
    bot = MemeGodBot(args.api_token, args.elections)
    if args.start is True:
        bot.start_listening()
    if args.call_winner is True:
        bot.call_winner(args.chat_id)

if __name__ == '__main__' :
    main()
