==========
Statements
==========

When we start talking about financials and accounting, many times we are associate with definition of creative accounting, povisions, adjustments or acceptable deviation but the one think is really stable and unchanged "History". Scrooge provide create historical statements manually. One way is just create report for past date but for be sure that historical raporte will be not changed, create a statement.

Logic for create statements is as simple as can be. Generated report is converted to JSON and saved in database. JSON cannot be changed by users so, it can give you safe, your historical report will be saved and unchanged forever. This simple case protects us from human mistakes like change invoice cost for the past date or rebuild/upgrade custom plugins. This is a really important case when system is fexibility and allows you to create custom and dedicated logic.
