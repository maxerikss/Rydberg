# rydbergHelper.py
This python script will read the API of Zettle and should create latex files for the menu items in stock, this is mainly for Beer and Cider, but also wine, since these are the only items we track the inventory of in Zettle.

## What to fix - higher priority
[x] Some way to set beer of the week

[] Some way to fix the standard Beers

[] This is more of a Zettle problem, but some way to integrate beer styles. A good way is probably by using Zettle categories as styles. So instead of Hofbräu.category = Beer, we get Hofbräu.category = Lager.

## What to fix - lower priority

[] The program right know authenticates everytime it is run, however the authentication key is valid for two hours so it might be good to save it so it is not requested as often