**Intro**: This repo will save you the time of calculating your Reward Points each month post getting your Credit Card Bill on email. See below video for more details.

https://user-images.githubusercontent.com/29705160/126617769-64261624-7d57-4c55-ac22-b7e9ded2c4af.mp4

**Requirements**: 
1. Id & Password of the email where the bill is sent.
2. Password to decrypt the bill. (Usually it is First four characters of your name + Your DOB in DDMM format)

**Note**: Right now, it supports reward point calculation for only Amazon Pay ICICI Credit Card. Will add more credit cards soon as and when time permits. 

**How To Install**: 
1. Download/ Clone this repo.
2. Now run the following command to install all the required libraries.     
        ``` pip install requirements.txt ```
3. Go to Amazon ICICI directory and set the DIRECTORY to the absolute path where you want to save the generated CSV file. 
4.  and run the below command. MONTH = month when the Credit Card bill was mailed.  
        ``` python3 install calculateRewardPoints.py MONTH ```
5. Tadaaa. A CSV with the individual reward point calculation is created at DIRECTORY.
