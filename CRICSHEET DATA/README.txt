All ICC Women's T20 World Cup match data in CSV format
======================================================

The background
--------------

As an experiment, after being asked by a user of the site, I started
converting the YAML data provided on the site into a CSV format. That
initial version was heavily influenced by the format used by the baseball
project Retrosheet. I wasn't sure of the usefulness of my CSV format, but
nothing better was suggested so I persisted with it. Later Ashwin Raman
(https://twitter.com/AshwinRaman_) send me a detailed example of a format
he felt might work and, liking what I saw, I started to produce data in
a slightly modified version of that initial example.

This particular zip folder contains the CSV data for...
  All ICC Women's T20 World Cup matches
...for which we have data.

How you can help
----------------

Providing feedback on the data would be the most helpful. Tell me what you
like and what you don't. Is there anything that is in the JSON data that
you'd like to be included in the CSV? Could something be included in a better
format? General views and comments help, as well as incredibly detailed
feedback. All information is of use to me at this stage. I can only improve
the data if people tell me what does works and what doesn't. I'd like to make
the data as useful as possible but I need your help to do it. Also, which of
the 2 CSV formats do you prefer, this one or the original? Ideally I'd like
to settle on a single CSV format so what should be kept from each?

Finally, any feedback as to the licence the data should be released under
would be greatly appreciated. Licensing is a strange little world and I'd
like to choose the "right" licence. My basic criteria may be that:

  * the data should be free,
  * corrections are encouraged/required to be reported to the project,
  * derivative works are allowed,
  * you can't just take data and sell it.

Feedback, pointers, comments, etc on licensing are welcome.

The format of the data
----------------------

Full documentation of this CSV format can be found at:
  https://cricsheet.org/format/csv_ashwin/
but the following is a brief summary of the details...

This format consists of 2 files per match, although you can get all of
the ball-by-ball data from just one of the files. The files for a match
are named <id>.csv (for the ball-by-ball data), and <id>_info.csv (for
the match info), where <id> is the Cricinfo id for the match. The
ball-by-ball file contains one row per delivery in the match, while the
match info file contains match information such as dates the match was
played, the outcome, and lists of the players involved in the match.

The match info file format
--------------------------

The info section contains the information on the actual match, such as
when and where it was played, any event it was part of, the type of
match etc. The fields included in the info section will each appear as
one or more rows in the data. Some of the fields are required, whereas
some are optional. If a field has multiple values, such as team, then
each value will appear on a row of it's own.

The ball-by-ball file format
----------------------------

The first row of each ball-by-ball CSV file contains the headers for the
file, with each subsequent row providing details on a single delivery.
The headers in the file are:

  * match_id
  * season
  * start_date
  * venue
  * innings
  * ball
  * batting_team
  * bowling_team
  * striker
  * non_striker
  * bowler
  * runs_off_bat
  * extras
  * wides
  * noballs
  * byes
  * legbyes
  * penalty
  * wicket_type
  * player_dismissed
  * other_wicket_type
  * other_player_dismissed

Most of the fields above should, hopefully, be self-explanatory, but some may
benefit from clarification...

"innings" contains the number of the innings within the match. If a match is
one that would normally have 2 innings, such as a T20 or ODI, then any innings
of more than 2 can be regarded as a super over.

"ball" is a combination of the over and delivery. For example, "0.3" represents
the 3rd ball of the 1st over.

"wides", "noballs", "byes", "legbyes", and "penalty" contain the total of each
particular type of extras, or are blank if not relevant to the delivery.

If a wicket occurred on a delivery then "wicket_type" will contain the method
of dismissal, while "player_dismissed" will indicate who was dismissed. There
is also the, admittedly remote, possibility that a second dismissal can be
recorded on the delivery (such as when a player retires on the same delivery
as another dismissal occurs). In this case "other_wicket_type" will record
the reason, while "other_player_dismissed" will show who was dismissed.

Matches included in this archive
--------------------------------

2026-07-05 - international - T20 - female - 1490709 - England vs Australia
2026-07-02 - international - T20 - female - 1490708 - England vs South Africa
2026-06-30 - international - T20 - female - 1490707 - West Indies vs Australia
2026-06-28 - international - T20 - female - 1490706 - India vs Australia
2026-06-28 - international - T20 - female - 1490705 - Bangladesh vs South Africa
2026-06-27 - international - T20 - female - 1490704 - New Zealand vs England
2026-06-27 - international - T20 - female - 1490703 - West Indies vs Ireland
2026-06-27 - international - T20 - female - 1490702 - Pakistan vs Netherlands
2026-06-26 - international - T20 - female - 1490701 - Scotland vs Sri Lanka
2026-06-25 - international - T20 - female - 1490700 - South Africa vs Netherlands
2026-06-25 - international - T20 - female - 1490699 - Bangladesh vs India
2026-06-24 - international - T20 - female - 1490698 - England vs West Indies
2026-06-23 - international - T20 - female - 1490697 - Australia vs Pakistan
2026-06-23 - international - T20 - female - 1490696 - Ireland vs Sri Lanka
2026-06-23 - international - T20 - female - 1490695 - Scotland vs New Zealand
2026-06-21 - international - T20 - female - 1490694 - India vs South Africa
2026-06-21 - international - T20 - female - 1490693 - Sri Lanka vs West Indies
2026-06-20 - international - T20 - female - 1490692 - England vs Scotland
2026-06-20 - international - T20 - female - 1490691 - Bangladesh vs Pakistan
2026-06-20 - international - T20 - female - 1490690 - Australia vs Netherlands
2026-06-19 - international - T20 - female - 1490689 - New Zealand vs Ireland
2026-06-18 - international - T20 - female - 1490688 - West Indies vs Scotland
2026-06-17 - international - T20 - female - 1490687 - Pakistan vs South Africa
2026-06-17 - international - T20 - female - 1490686 - India vs Netherlands
2026-06-17 - international - T20 - female - 1490685 - Bangladesh vs Australia
2026-06-16 - international - T20 - female - 1490684 - Ireland vs England
2026-06-16 - international - T20 - female - 1490683 - New Zealand vs Sri Lanka
2026-06-14 - international - T20 - female - 1490682 - India vs Pakistan
2026-06-14 - international - T20 - female - 1490681 - Netherlands vs Bangladesh
2026-06-13 - international - T20 - female - 1490680 - New Zealand vs West Indies
2026-06-13 - international - T20 - female - 1490679 - Australia vs South Africa
2026-06-13 - international - T20 - female - 1490678 - Scotland vs Ireland
2026-06-12 - international - T20 - female - 1490677 - England vs Sri Lanka
2024-10-20 - international - T20 - female - 1432444 - New Zealand vs South Africa
2024-10-18 - international - T20 - female - 1432443 - New Zealand vs West Indies
2024-10-17 - international - T20 - female - 1432442 - Australia vs South Africa
2024-10-15 - international - T20 - female - 1432441 - England vs West Indies
2024-10-14 - international - T20 - female - 1432440 - New Zealand vs Pakistan
2024-10-13 - international - T20 - female - 1432439 - Australia vs India
2024-10-13 - international - T20 - female - 1432438 - Scotland vs England
2024-10-12 - international - T20 - female - 1432437 - Bangladesh vs South Africa
2024-10-12 - international - T20 - female - 1432436 - Sri Lanka vs New Zealand
2024-10-11 - international - T20 - female - 1432435 - Pakistan vs Australia
2024-10-10 - international - T20 - female - 1432434 - Bangladesh vs West Indies
2024-10-09 - international - T20 - female - 1432433 - India vs Sri Lanka
2024-10-09 - international - T20 - female - 1432432 - South Africa vs Scotland
2024-10-08 - international - T20 - female - 1432431 - Australia vs New Zealand
2024-10-07 - international - T20 - female - 1432430 - South Africa vs England
2024-10-06 - international - T20 - female - 1432429 - Scotland vs West Indies
2024-10-06 - international - T20 - female - 1432428 - Pakistan vs India
2024-10-05 - international - T20 - female - 1432427 - England vs Bangladesh
2024-10-05 - international - T20 - female - 1432426 - Sri Lanka vs Australia
2024-10-04 - international - T20 - female - 1432425 - New Zealand vs India
2024-10-04 - international - T20 - female - 1432424 - West Indies vs South Africa
2024-10-03 - international - T20 - female - 1432423 - Pakistan vs Sri Lanka
2024-10-03 - international - T20 - female - 1432422 - Bangladesh vs Scotland
2023-02-26 - international - T20 - female - 1338062 - Australia vs South Africa
2023-02-24 - international - T20 - female - 1338061 - South Africa vs England
2023-02-23 - international - T20 - female - 1338060 - Australia vs India
2023-02-21 - international - T20 - female - 1338059 - Bangladesh vs South Africa
2023-02-21 - international - T20 - female - 1338058 - England vs Pakistan
2023-02-20 - international - T20 - female - 1338057 - India vs Ireland
2023-02-19 - international - T20 - female - 1338056 - New Zealand vs Sri Lanka
2023-02-19 - international - T20 - female - 1338055 - West Indies vs Pakistan
2023-02-18 - international - T20 - female - 1338054 - South Africa vs Australia
2023-02-18 - international - T20 - female - 1338053 - England vs India
2023-02-17 - international - T20 - female - 1338052 - Ireland vs West Indies
2023-02-17 - international - T20 - female - 1338051 - New Zealand vs Bangladesh
2023-02-16 - international - T20 - female - 1338050 - Sri Lanka vs Australia
2023-02-15 - international - T20 - female - 1338049 - Pakistan vs Ireland
2023-02-15 - international - T20 - female - 1338048 - West Indies vs India
2023-02-14 - international - T20 - female - 1338047 - Bangladesh vs Australia
2023-02-13 - international - T20 - female - 1338046 - South Africa vs New Zealand
2023-02-13 - international - T20 - female - 1338045 - Ireland vs England
2023-02-12 - international - T20 - female - 1338044 - Bangladesh vs Sri Lanka
2023-02-12 - international - T20 - female - 1338043 - Pakistan vs India
2023-02-11 - international - T20 - female - 1338042 - Australia vs New Zealand
2023-02-11 - international - T20 - female - 1338041 - West Indies vs England
2023-02-10 - international - T20 - female - 1338040 - Sri Lanka vs South Africa
2020-03-08 - international - T20 - female - 1173070 - Australia vs India
2020-03-05 - international - T20 - female - 1173069 - Australia vs South Africa
2020-03-03 - international - T20 - female - 1173066 - Pakistan vs Thailand
2020-03-02 - international - T20 - female - 1173065 - Australia vs New Zealand
2020-03-02 - international - T20 - female - 1173064 - Bangladesh vs Sri Lanka
2020-03-01 - international - T20 - female - 1173063 - England vs West Indies
2020-03-01 - international - T20 - female - 1173062 - Pakistan vs South Africa
2020-02-29 - international - T20 - female - 1173061 - India vs Sri Lanka
2020-02-29 - international - T20 - female - 1173060 - Bangladesh vs New Zealand
2020-02-28 - international - T20 - female - 1173059 - England vs Pakistan
2020-02-28 - international - T20 - female - 1173058 - South Africa vs Thailand
2020-02-27 - international - T20 - female - 1173057 - Australia vs Bangladesh
2020-02-27 - international - T20 - female - 1173056 - India vs New Zealand
2020-02-26 - international - T20 - female - 1173055 - Pakistan vs West Indies
2020-02-26 - international - T20 - female - 1173054 - England vs Thailand
2020-02-24 - international - T20 - female - 1173053 - Bangladesh vs India
2020-02-24 - international - T20 - female - 1173052 - Australia vs Sri Lanka
2020-02-23 - international - T20 - female - 1173051 - England vs South Africa
2020-02-22 - international - T20 - female - 1173050 - New Zealand vs Sri Lanka
2020-02-22 - international - T20 - female - 1173049 - Thailand vs West Indies
2020-02-21 - international - T20 - female - 1173048 - Australia vs India
2018-11-24 - international - T20 - female - 1150555 - England vs Australia
2018-11-22 - international - T20 - female - 1150554 - India vs England
2018-11-22 - international - T20 - female - 1150553 - Australia vs West Indies
2018-11-18 - international - T20 - female - 1150552 - South Africa vs Bangladesh
2018-11-18 - international - T20 - female - 1150551 - England vs West Indies
2018-11-17 - international - T20 - female - 1150550 - Ireland vs New Zealand
2018-11-17 - international - T20 - female - 1150549 - India vs Australia
2018-11-16 - international - T20 - female - 1150548 - West Indies vs Sri Lanka
2018-11-16 - international - T20 - female - 1150547 - South Africa vs England
2018-11-15 - international - T20 - female - 1150546 - New Zealand vs Pakistan
2018-11-15 - international - T20 - female - 1150545 - India vs Ireland
2018-11-14 - international - T20 - female - 1150544 - West Indies vs South Africa
2018-11-14 - international - T20 - female - 1150543 - Sri Lanka vs Bangladesh
2018-11-13 - international - T20 - female - 1150542 - Australia vs New Zealand
2018-11-13 - international - T20 - female - 1150541 - Pakistan vs Ireland
2018-11-12 - international - T20 - female - 1150540 - Sri Lanka vs South Africa
2018-11-12 - international - T20 - female - 1150539 - Bangladesh vs England
2018-11-11 - international - T20 - female - 1150538 - Ireland vs Australia
2018-11-11 - international - T20 - female - 1150537 - Pakistan vs India
2018-11-09 - international - T20 - female - 1150535 - West Indies vs Bangladesh
2018-11-09 - international - T20 - female - 1150534 - Australia vs Pakistan
2018-11-09 - international - T20 - female - 1150533 - India vs New Zealand
2016-04-03 - international - T20 - female - 951419 - Australia vs West Indies
2016-03-31 - international - T20 - female - 951417 - New Zealand vs West Indies
2016-03-30 - international - T20 - female - 951415 - Australia vs England
2016-03-28 - international - T20 - female - 951413 - South Africa vs Sri Lanka
2016-03-27 - international - T20 - female - 951411 - England vs Pakistan
2016-03-27 - international - T20 - female - 951409 - India vs West Indies
2016-03-26 - international - T20 - female - 951407 - New Zealand vs South Africa
2016-03-26 - international - T20 - female - 951405 - Australia vs Ireland
2016-03-24 - international - T20 - female - 951403 - Bangladesh vs Pakistan
2016-03-24 - international - T20 - female - 951401 - Australia vs Sri Lanka
2016-03-24 - international - T20 - female - 951399 - England vs West Indies
2016-03-23 - international - T20 - female - 951397 - Ireland vs South Africa
2016-03-22 - international - T20 - female - 951395 - India vs England
2016-03-21 - international - T20 - female - 951393 - Australia vs New Zealand
2016-03-20 - international - T20 - female - 951391 - Sri Lanka vs Ireland
2016-03-20 - international - T20 - female - 951389 - Bangladesh vs West Indies
2016-03-19 - international - T20 - female - 951387 - India vs Pakistan
2016-03-18 - international - T20 - female - 951385 - Australia vs South Africa
2016-03-18 - international - T20 - female - 951383 - Ireland vs New Zealand
2016-03-17 - international - T20 - female - 951381 - Bangladesh vs England
2016-03-16 - international - T20 - female - 951379 - Pakistan vs West Indies
2016-03-15 - international - T20 - female - 951377 - New Zealand vs Sri Lanka
2016-03-15 - international - T20 - female - 951375 - India vs Bangladesh
2014-04-06 - international - T20 - female - 683015 - Australia vs England
2014-04-04 - international - T20 - female - 683013 - England vs South Africa
2014-04-03 - international - T20 - female - 718467 - Bangladesh vs Ireland
2014-04-03 - international - T20 - female - 718465 - Pakistan vs Sri Lanka
2014-04-03 - international - T20 - female - 683011 - Australia vs West Indies
2014-04-02 - international - T20 - female - 683009 - India vs Pakistan
2014-04-02 - international - T20 - female - 683007 - New Zealand vs Sri Lanka
2014-04-01 - international - T20 - female - 683005 - India vs West Indies
2014-04-01 - international - T20 - female - 683003 - Bangladesh vs Sri Lanka
2014-03-31 - international - T20 - female - 683001 - New Zealand vs South Africa
2014-03-31 - international - T20 - female - 682999 - Ireland vs Pakistan
2014-03-30 - international - T20 - female - 682997 - England vs Sri Lanka
2014-03-30 - international - T20 - female - 682995 - Bangladesh vs India
2014-03-29 - international - T20 - female - 682993 - Australia vs Pakistan
2014-03-29 - international - T20 - female - 682991 - Ireland vs South Africa
2014-03-28 - international - T20 - female - 682989 - Sri Lanka vs West Indies
2014-03-27 - international - T20 - female - 682985 - New Zealand vs Pakistan
2014-03-26 - international - T20 - female - 682981 - England vs India
2014-03-26 - international - T20 - female - 682979 - Bangladesh vs West Indies
2014-03-25 - international - T20 - female - 682975 - Ireland vs New Zealand
2014-03-24 - international - T20 - female - 682973 - India vs Sri Lanka
2014-03-24 - international - T20 - female - 682971 - England vs West Indies
2014-03-23 - international - T20 - female - 682967 - Australia vs New Zealand

Consolidated data
-----------------

You may notice that there is an extra CSV file in this archive, called
"all_matches.csv". This file, as the name suggests, contains all of the
ball-by-ball data for matches from the archive in a single CSV. Hopefully
it will make use of the data easier in some cases.

Further information
-------------------

You can find all of our currently available data at https://cricsheet.org/

You can contact me via the following methods:
  Email   : stephen@cricsheet.org
  Mastodon: @cricsheet@deeden.co.uk
