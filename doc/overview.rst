========
Overview
========

What is Scrooge? The simple answer for this question is "Billing system for corporations". How does it work? Spread the cost of devices, energy, network etc. to the clients. For example, if you are CO or main accountant of huge company where there are many devices, projects and people, probably you need to know how many resources is used by each of team or worker. Maybe you need to charge some people or just need financial statements for make any important decision. It is no metter why you need financial statement, Scrooge give you it but the first thing you need to know is that Scrooge is neither excel nor advanced calculator, Scrooge works on data collected from many devices or supply by many people. It is some kind of system to calculate and display results of collected or supplied data with many additional features that make it easier to use.

.. image:: images/mainidea.png

As you can see, we can distinguish three main parts of architecture. Collects data, supply invoce costs and generate reports. This is the main idea of Scrooge. Accountants every month supply all costs of invoice. Collects plugin system collects data from many devices or designated people supply data. Report section calculate everything and display it like a report where costs from invoces, based on devices or teams usages are spread to predefined clients.

Second goal of Scrooge is flexibility of system. Look at the picture and find each cloud where description starts with "report". So? there are two places, one of them is for collets data and second one is for generating reports. Thats means that we don't impose one way or logic to generate or collect data. Of course, we have suggested usage but it is not required. There is a couple of rules how to communicate plugins with core but algorithm of collects or report data is yours.

As you probably know, all financial statements must be historical imprinted as subtitles carved into the rock. Scrooge contains his own database where each of incomming data is collected and imprinted forever in the basic form.

.. image:: images/usages.png

To be sure that generated reports will be the same forever you can create a statement. Statemets are saved in database as a json with full data from report so, if your crash your database manually and some of data disappear, you can still go back to old report by choose a correct statement from menu.

Ok, but what if some of our clients generate costs of another clients? It is not a problem for the Scrooge. For this case we have services. Service is some kind of bag where many clients are grouped and total cost of this bag is spreaded to another users. One thing that you need to do is supply information on what part of cost must be distributed to another client.

.. image:: images/services.png

Scrooge contains a few base plugins and tools for programmers so, you don't need create everything on the begin. The most complicated parts are coded by our own programmers so, there is a few methods and function ready to use but more about this you can find in source code and doctrings. 

In sum, total client cost include 3 main parts, base cost, cost of another clients and extra costs. The last one cost is manually added costs and it is for example cost of liceans. So, as you can see Scrooge give you possibility to implement all kinds of costs what the huge company generate. Maybe it is not easy to impelement system but it is really flexibility and advenced business application.
