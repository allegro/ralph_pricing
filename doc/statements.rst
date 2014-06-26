==========
Statements
==========

When we start talking about financials and accounting, we may come across definitions of creative accounting, provisions, adjustments or acceptable deviation, but the one think is really stable and unchanged "History". Scrooge provides an opportunity to create historical statements manually. You may just create a report for the past date but to be sure that the historical raport will be not changed, you may create a statement.

The logic for creating statements is as simple as possible. A report is converted to JSON and saved in the database. JSON cannot be changed by users, so you will be sure that your historical report will be saved and unchanged forever. This simple case protects us from human mistakes like changing an invoice cost for the past date or rebuilding/upgrading custom plugins. This is a really important case when the system is flexible and allows you to create a custom and dedicated logic.

