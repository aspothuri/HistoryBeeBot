Hi everyone, this is my History Bowl bot that allows users to run a full History Bee round with scorecard and question reading functionality.

This discord bot allows users to run a full History Bee round with every functionality. This includes question reading, grading, and scorekeeping for several players. It is easily customizable and simple to set up.

To get started make sure to clone the github using

```
git clone https://github.com/aspothuri/HistoryBeeBot.git
```

If you don't already have [Python](https://www.python.org/downloads/) installed, please do so. Additionally, ensure you have [pip](https://pip.pypa.io/en/stable/installation/) set up. After these initial steps, open up the directory in a terminal of your choice.

Run 

```
pip install -r requirements.txt
```

to install all necessary packages for this project.

Finally, make sure to create your own discord bot, invite it to your server and replace the key in the .env file with the secret access key.

Then run 

```
python discord_bot.py
```

and enjoy the game.




The following are the currently available commands that can be used with the bot.

`/start_game`: starts a game in the provided voice channel using the provided standard [History Bee files](https://www.iacompetitions.com/resources-national-history-bee/).

`/end_game`: ends that exact game and deletes the files used

`/next_question`: proceeds to the next question or skips to a specified tossup if one is given

`/buzz`: allows a player to queue a buzz and provides 5 seconds before the timer runs out

`/scoreboard`: provides a formatted scoreboard of every user, 10 points for correct and -5 for an incorrect interrupt


Most edge cases are accounted for but there are still likely some bugs. Please let me know at abhitroll@gmail.com if you find any major issues and I'll do my best to fix them

Thank you all and good luck!!

