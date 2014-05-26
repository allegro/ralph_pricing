===================
Costs & Extra costs
===================
For calculate total cost of venture/usage we need add two type of costs. The most important and first of them is base usages cost. Base costs are used to calculate physical (real) cost of ventures or services so, when one of base costs will not be entered or given cost is not correct, real cost of venture is distorted. Second one costs are named as extra costs and there are additional costs like a software license etc. Cost and extracosts should not be changed for the past time period.

Costs
~~~~~

.. image:: images/costs.png

This type of costs is responsible for calculate real costs of usages and ventures. Usually, we have invoice costs but it is not a rule. When base costs will not be entered correctly, then all of calculations are distored (and this is the most important thing to remember). Second one thing to remember is dates continuity. For example if you enter invoce cost from April you should give a date from 2014-04-01 to 2014-04-30 and then when you enter invoce cost from May, you should type start from 2014-05-01. Costs contains two error types:


No price
  When base usage price is not entered at all for given time period for generated report.
  For example: Someone forgot give invoce cost from May.

Incomplete price
  When given price have no dates continuity for given time period for generated report.
  For example: Given cost for April is from 2014-04-01 to 2014-04-20 and second one cost is from 2014-04-22 to 2014-04-30. There is not price for 2014-04-21.

These errors will be visible on generated report in appropriate cells.

Extra costs
~~~~~~~~~~~

Extra costs was created for additional costs like a software license etc. Extracost are use to past any unconventional costs to report and total cost of services. The most important to remember is the enter costs convetion. Each extracost cost entered to scrooge is a monthly cost but algorithm calculate daily cost of given extracost and create daily imprint of it. Lets analyze the story:

"Department of internal solutions" in May ordered 10 new keyboards for 3000$. For smooth administrations, cost of keyboards start calculate on 1 June so, daily cost of this order is 100$ (3000$/30days) and 10$ per each keyboard. At the same time, "Python Department" order 20 keyboards by 3000$ (Daily cost 3000/30=100) but this time each keyboard cost only 5$. On 15 June Pythons programers make a deal with people from internal solutions, they transfer 5 cheaper keyboards for 5 expensive keyboards. So whats look like monthly statemenet for orders for this two departments? 

::

    Department of internal solutions:
    
    1-15 June = 100$*15days = 1500$                       # daily cost = 100$
    16-30 June = 50$*15days + 25$*15days = 1125$          # daily cost = 75$
    Total cost = 2625$

    Python programmers:
    
    1-15 June = 100$*15days = 1500$                       # daily cost = 100$
    16-30 June = 75$*15days + 50$*15days = 1875$          # daily cost = 125$
    Total cost = 3375$


So, based on current monthly cost, daily cost of each extracost is calculate and imprint. At the begin (befor transfer) daily cost was the same (each of demartments buy something for 3000$) but after transfer dailycost was changed becouse python programmers got 5 expensive keybords and lost 5 cheaper keyboards and vice versa for internal solutions demartment.
