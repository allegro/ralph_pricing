========
Overview
========

What is Scrooge? The simple answer for this question is "Billing system for corporations". How it works? Spread the cost of devices, energy, network etc. to the clients. For example, if you are CO or main accountant of huge company where there is many devices, projects and people, probably you need to know how many resources is used by each of team or worker. Maybe you need charge costs for some people or just you need financial statements for make any important decision. It is no metter why you need financial statement, scrooge give you it but the first thing you need to know the scrooge is not any excel, word or advenced calculator, scrooge works on data collected from many devices or supply by many people. It is some kind of system to calculate and display results of collected or supplied data with many additional feature that make it easier to use.

.. image:: images/mainidea.png

As you can see, we can distinguish three main parts of architecture. Collects data, supply invoce costs and generate reports. This is the main idea of scrooge. Accountants every month supply all costs of invoices. Collects plugin system collects data from many devices or designated people supply data. Report section calculate everything and display it like a report where costs from invoce, based on devices or teams usages are spread by predefined clients.

Second goal of scrooge is flexibility of system. Look on the picture and find each cloud where description starts on "report". So? there are two places, one of them is for collets data and second one is for generating reports. Thats mean that we not impose one way or logic to generate or collect data. Of course, we have suggested usage but it is not required. There is a couple of rules how to communicate plugins with core but algorithm of collects or report data is yours.

As you probably know, all financial statements must be historical imprinted as subtitles carved into the rock. Scrooge contains his own database where each of incomming data are collected and imprinted forever in the basic form.

.. image:: images/usages.png

But for be sure that generated reports will be the same forever you can create a statement. Statemets are write in database like a json with full data from report so, if your crash your database manually and some of data disapear, you still back to your old report by choose a correct statement from menu.

Ok, but what if some of our clients generate costs of another clients? It is not a problem for the scrooge. For this case we have services. Service is some kind of bag where are group many clients and total cost of this bag is spread to anyother users. One thing what you need to do is supply information on what part of cost must be route to another client.

.. image:: images/services.png

Scrooge contains a few base plugins and tools for programmers so, you don't need create everything on the begin. The most complicated parts are coded by our own programmers so, there is a few methods and function ready to use but more about this you can find in source code and doctrings. 

In sum, total client cost include 3 main parts, base cost, cost of another clients and extra costs. The last one cost is manually added costs and it is for example cost of liceans. So, as you can see scrooge give you possibility to implement all kinds of costs what the huge company generate. Maybe it is not easy to impelement system but it is really flexibility and advenced business application.
