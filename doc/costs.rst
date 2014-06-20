===================
Costs & Extra costs
===================
To calculate the total cost of venture/usage, we need to add two types of costs. The most important and the first of them is the base usages cost. Base costs are used to calculate the actual (real) cost of ventures or services, so when any of the base costs is not entered or any cost is not correct, the real cost of venture is distorted. The other costs are called extra costs with additional costs of e.g. a software license. The costs and extra costs should not be changed for the past period.


Costs
~~~~~

.. image:: images/costs.png

This type of costs is used to calculate real costs of usages and ventures. Usually, we have invoice costs, but it is not a rule. When base costs are not entered correctly, all of the calculations are distored (and this is the most important thing to remember). You should also remember about continuity of dates. For example, if you enter an invoice cost from April, you should enter the date from 2014-04-01 to 2014-04-30 and when you enter an invoice cost from May, you should start from 2014-05-01. You may see two error types for costs:



No price
  It appears when the base usage price is not entered at all for a given time period for a report. For example: someone has forgotten to enter the invoice cost from May.


Incomplete price
  It appears when a given price has no continuity of dates for a given time period for areport. For example: the cost for April is from 2014-04-01 to 2014-04-20 and the second one is from 2014-04-22 to 2014-04-30. There is no price for 2014-04-21.


These errors will be visible in the report in appropriate cells.

Extra costs
~~~~~~~~~~~

Extra costs were created for additional costs such as a software license. Extra costs are used to provide any unconventional costs to the report and to the total cost of services. It is important to enter the costs convention. Each extra cost entered to Scrooge is a monthly cost, but the algorithm calculates a daily cost and generates a daily print-out. Let’s analyze the following story:

In May the Internal Solutions Department ordered 10 new keyboards for
$3,000. For smooth administration, the cost of keyboards started to be calculated on 1 June, so the daily cost of this order is $100 ($3,000/30 days) and $10 per each keyboard. At the same time, The Python Department ordered 20 keyboards for $3,000 (daily cost: 3,000/30=100), but this time each keyboard costs only $5. On 15 June Python software developers made a deal with people from internal solutions to exchange 5 cheaper keyboards for 5 expensive keyboards. As a result, what is the monthly statemenet for the orders of these two departments
?

::

    Internal Solutions Department:

    1-15 June = $100 * 15 days = $1500                    # daily cost = $100
    16-30 June = $50 * 15 days + $25 * 15 days = $1125    # daily cost = $75
    Total cost = $2625

    Python programmers:

    1-15 June = $100 * 15 days = $1500                    # daily cost = $100
    16-30 June = $75 * $15 days + $50 * 15 days = $1875   # daily cost = $125
    Total cost = $3375


Therefore, based on the current monthly cost, the daily cost of each extra cost is calculated and printed. At the beginning (before the exchange), the daily cost was the same (each of departments bought products for $3,000) but after the exchange the daily cost was changed, because Python software developers received 5 expensive keybords and gave away 5 cheaper keyboards and vice versa for the Internal Solutions Department.
