# correlations_webApp
 
I was inspired by "Paul Tudor Jones - Trader Documentary 1987". Where they run correlations between the bull market they had at the time and the one in the 1920s. The correlation turned out to be over 90% and they indeed predicted the 1987 Crash.

The goal of this project was to automatize what they did in the documentary. 

In the app we can find:
- Instrument: the instrument to run the scanner on.
- Time frame: the size of the data you want to scan. 
- Lookback: the number of days you want to scan through.
- Accuracy: the step of the scanner. A 1 week step means the scanner will loop with more frequency than with a 1 month step. A shorter step makes the scanner run slower, but could result in more occurrences.
- Correlation: to filter highly correlated occurrences.

Example:
  Instrument    Time frame   Lookback   Accuracy   Correlation
S&P 500 Futures   1 month     2 years     1 week     Over 0.5
--> Scan a time frame of 1 month through 2 years of data with a step of 1 week. Show me the occurrences with correlation higher than 0.5.

Then we click on "Send" and the scanner starts. We can stop the scanner at any time by clicking on "Reset" and it will show us all the occurrences found since it started.

Once the "Send" button is clicked, the app checks if today is a new day, if so it downloads new data from Quandl and updates our database. I used SQLite beacuse of its simplicity.

Data is normalized and then the app calculates the %Change.

The scanner calculates correlations and the ones that make the cut are sent to a function that takes the data and builds a chart. Plotting current time frame, the occurrence, and the followup of that occurrence.

I chose the Pearson correlation coefficient formula
(https://wikimedia.org/api/rest_v1/media/math/render/svg/f76ccfa7c2ed7f5b085115086107bbe25d329cec)



Live test video because Github Pages doesn't allow Python3-Flask webapps: 
https://youtu.be/9CBFMtaiaX4

[![Live test](https://img.youtube.com/vi/9CBFMtaiaX4/0.jpg)](https://youtu.be/9CBFMtaiaX4)
