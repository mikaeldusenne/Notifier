# Notifier

This simple application provides a python framework to ease the creation of notification modules.

The `NotifierMailer` directory contains the main script,
ant the `apps` directory contains some examples.

You can:

- check an API / scrape a website (or any other source of data)
- extract relevant data from it
- compare since last run (the previous run is saved in the filesystem)
- provide a predicate function to trigger notifications based on the data
- run different programs when the predicate function is successfully activated, such as mail sending, desktop notifications

The architecture's goal is to be succint and as modular as possible, and to accomodate a large variety of tasks with a minimum of effort.

It comes particularily handful for tasks where I would otherwise "hit F5 and reload some web page to check something": instead I quicky write the scraping code + setup the notifications I want, and add the script to my cron tasks, and voilà, I just need to wait for the notification to arrive.

disclaimer: this program is not system agnostic and currently still relies of my personal setup and it's various dependencies to be setup.


