# Network Partitioning Effects on Ripple Transactions

Network partitioning is a serious problem for blockchains: a partitioned network cannot reach consensus on the state of the chain. But how likely is such an attack? Research has already shown such attacks are possible on Bitcoin, but most other protocols ignore such attacks. In fact, most blockchain protocols analyze the traffic patterns in the overlay communication network, but disregard the actual BGP (Border Gateway Protocol) path taken by traffic, on an ISP level. That’s precisely what we want to look at first. We then want to see whether restricting the set of communicating blockchain peers greatly diminishes the consequences of an attack.
In this project, we will first look at real Internet traffic traces from CAIDA, to see whether traffic between two nearby peers stay local. For example, if both peers are in Switzerland, does their traffic transit only Swiss ISPs (Internet Service Providers) or does it cross the border? Perhaps this sounds surprising, but economic incentives of ISPs make such scenarios likely. 
Then, we’ll do a cross-analysis of network traffic and Ripple transactions to understand the effects of potential network partitioning (think of it as an Internet shutdown between Europe and the US). That’s a bit similar to the Ethereum community chat of the World War 3 scenario. Which / how many past transactions would have been affected? 

# Code Submission

The code related to the report and the presentation can be found in the master branch. <br>
1) Caida contains the processing of the Caida dataset <br>
2) Ripple contains the processing of the Ripple API (gateways, transactions, exchange rate) <br>
3) Gephi contains the processing to display the graph on a map <br>
4) report contains the report and the presentation <br>
All the notebooks are already executed, you can see them directly on github. Each notebook contains a step-by-step explaination of my process. <br>
<br>
Since this project is mostly a data analysis project, an important job of exploration has been done. If you want to go more into the details of my exploration. You can access this link on the data_exploration branch https://github.com/dedis/student_19_ripple-partition/tree/ca3e40b48f9e344fad1cf57d41cbb508ba234e88. If you want to understand how I lead my project, you can access this google doc https://docs.google.com/document/d/1WRk7rECmT47KmHcoyUY3uNxciVELF7ARVYRz7mfUr4E/edit
