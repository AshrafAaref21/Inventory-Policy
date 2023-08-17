It's an Inventory Model Made by Python to take a Purchasing decision for about 50 SKUs according to our business parameters, Economy and Market uncertainties... 

<<This 50 SKUs = 25% of company Sales>>

Starting with Cleanings and Treating the Sales data '19 Months' and making analysis to allocate the expected mean of sales and its variance to allocate its a strategic SKU or not to get the minimum safety stock for each SKU according to its CSL (95% for strategic SKUs,.. down to 65% to not important SKUs)


Then I Calculated the Order Quantity according to its company limitations and our optimum Order Quantity.


Then we input our SKUs Cost,Price,Stock 'now' and grap all the data together in a dataframe to Create our Model Class


I Design The model as an Optimization Model to know how much should i order now according to all the needed Constraints …

Then I create a small code to initial the model and try if it possible with all the constraints and then release one constraint and try it again as many as we need to get the best solution according to our situation.


We used Oracle ERP System to set up our base stock for each SKU according to our analysis.


The Code takes only the SKU code that got an inventory Alert, the New SKUs Cost&Price if changed, And The Inventory Stock Now... And we got this data from our ERP System.

<<<It's an Snapshot in 12 Augest 2023>>>



Project in GitHub, Link >> https://lnkd.in/dM4y4qej

<<<It's an Snapshot in 12 Augest 2023>>>
THANKS FOR READING...!


