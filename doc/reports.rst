=======
Reports
=======
There are a few report types. The main one is called “Ventures report” being a billing report. Scrooge also contains other reports supporting the main report. For example, one of them shows venture usages for each day. The other one shows devices containing a selected venture. As you probably know, cost columns are not always enough as people want to know how, why and where the figures come from. One of the solutions is to create one huuuuge report with many columns and nested tables, but do you think it is will be clear enough for us? In my opinion, an experienced accountant may have a problem to analyse large statements and each mistake can be dangerous for strategic or tactical business plans. The other solution is to create categorized reports – in such case, we can use a few Scrooge reports.


To understand this section better, use a simple info card:

::

    Target:
        Description
    Actions:
        - First action
        - Second Action
        - ...

Ventures report
---------------

::

    Target:
        Show total cost of each venture
    Actions:
        - Generate financial billing
        - Create Statement
        - Download as CSV

You can have the main report, statement of costs or just a financial billing if you wish. Here, you will see all the costs for each venture. Columns contain the total cost of base usage, service usages and extra costs. Additionally, each service cost contains more details about each usage. Details are shown as count and cost column.

This view also gives you a possibility to generate a csv file and create a statement of report options. If you click Create statement or Download csv before the update, a report will be generated, so you don’t need to generate a report before creating a statement to download it to csv.


Devices report
--------------

::

    Target:
        Show all devices and their cost for single venture
    Actions:
        - Generate statement of devices for single venture
        - Create Statement
        - Download as CSV

This report shows you details for a single venture. This solution is used when someone comes to you and asks why his costs are so high. Then, you can generate a device report to show which devices are assigned to him and how much they cost. It is very important for big huge companies with e.g. one thousand ventures.


Ventures daily usages
---------------------

::

    Target:
        Show usage count differences between days
    Actions:
        - Generate usages count differences report
        - Create Statement
        - Download as CSV

This report is logically linked with device ventures changes, but we have separated it, because the two reports would look like a board with undefined numbers.

As a result, the ventures daily usages report shows you only numbers of changed usages in a selected time interval for all ventures. There are no details on which device was transfereed between two or more ventures. This is only comp of changes in our system and if you see any warnings or errors in changes and you need to verify what was changed, then you need to use the device ventures changes report.


Device ventures changes
-----------------------

::

    Target:
        Show information about transferring devices between ventures
    Actions:
        - Generate device transfer report
        - Create Statement
        - Download as CSV

This report shows how devices were transferred between ventures. The device ventures changes report is a supplement to the ventures daily usages. It is really useful when ventures contain many devices (for example two thousand) and many devices often change their owners. This report shows you change details for a selected date.

