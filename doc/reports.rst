=======
Reports
=======
There are a few types of reports. The main report is named as 'Ventures report' and this is billing report. For improve, scrooge contains few more reports like a support for main report. For example one of them show as a count of venture usages for each day. Second one show as what devices contains choosen venture. As probably you know, columns with costs it is not enought for few cases, people want to know how, why and from comes this numbers. One of solution is create one huuuugeee report with many columns and nested tables but what do you think? it is enought clear for human eyes? In my opinion, experienced accountant can have a problems with analyse huge statements but each mistake could be dangerous for strategic or tactical business plans. Second one solutions is create categorized reports and here we are a few scrooge reports.

For explain better this sections lest use simple info card:

::

    Destiny:
        Description

    Actions:
        - First action
        - Second Action
        - ...

Ventures report
---------------

::

    Destiny:
        Show total cost of each venture
    Actions:
        - Generate financial billing
        - Create Statement
        - Download as CSV

The main report, statement of costs or just a financial billing if you wish. Here we have all costs for each venture. Columns contains total cost of base usage, service usages and extra costs. Additional, each of service costs contains more details about each usage included in to. Details are represents as count and cost column. 

Also this view give you generate to csv and create a statement of generated report options. If you click create statement button or Download csv befor update then report will be generated so, you dont need generate report befor create statement of download it to csv.

Devices report
--------------

::

    Destiny:
        Show all devices and cost of them for single venture
    Actions:
        - Generate statement of devices for single venture
        - Create Statement
        - Download as CSV

Report show you details for single venture. This is solution for case when someone come to you and ask why his costs are so big. For people like this you can generate device report and show him what devices are assignet to him and how mutch they costs. This is a very important case for huge companies where is for example one thousand ventures.

Ventures daily usages
---------------------

::

    Destiny:
        Show usages count differences between few days
    Actions:
        - Generate usages count differences report
        - Create Statement
        - Download as CSV

This report is logicly linked with Device ventures changes but we separate it because results of this two reports tougether will looks like board with undefined numbers.

So, Ventures daily usages report show you only the numbers of changed usages in choose time interval for all ventures. There is no details about with device was transferet between two or more ventures. This is only comp of changes in our system and when you find any warnings or erros in changes and you need to verify what was changed then you need to use Device ventures changes report.

Device ventures changes
-----------------------

::

    Destiny:
        Show information about transferring  devices between ventures
    Actions:
        - Generate device transfer report
        - Create Statement
        - Download as CSV

This report show how devices transferred between ventures. Device ventures changes report is supplement of Ventures daily usages. It is really usefull when ventures contains many devices (for example two thousand) and many devices often change his owners. This report show you the most nested details about change for choosen date.
