All instructions relate to users using PyCharm. If you want to run everything from the command line / terminal
, adjust instructions accordingly.

I assume everyone has cloned the repo (like we did in the demo). If you haven't, or deleted your local copy of the
 repo, repeat those instructions to clone again.
 
 **Make sure the CDD project is opened in PyCharm**
 
### Step 1: Checkout The master Branch
 From PyCharm, go to the Menu Bar at the top
 
 Then go to VCS > Git > Branches
 
 Under "Remote Branches", click on "origin/master" and select "Checkout"

### Step 2: Download the Required Packages
> **Note:** I haven't figured out a way to do this solely through PyCharm

Within PyCharm, select "Terminal" from the Menu at the bottom. Run the following command:

```bash
$ pip install -r requirements.txt
```

### Step 3: Mark the "Algorithm(s) to Determine District Lines" Directory as "Sources Root"
> **Note:** This step is necessary in order to make sure all the module imports work across Python files.

I figured the best way to explain this one would be using a video:

The video is [here](https://drive.google.com/file/d/1-5rCzGbKPNUYaUmzKeajazv-IFK0cKka/view?usp=sharing)

### Step 4: Open the Driver Program
Open the redistrict_state.py file from [Algorithm(s) To Determine District Lines/redistrict/redistrict_state.py](<Algorithm(s) To Determine District Lines/redistrict/redistrict_state.py>)

### Step 5: Change Line 22
Currently, that line reads:

```python
state_list = ['RI']
```

Change the list on the right hand side of the ```=``` with your list of state assignments. The assignments are as
 follows:
 
| Team Member   | List                                                   
| ------------- |:-------------:
| Adam          | ```['CT', 'MD', 'TN', 'AL', 'GA', 'WA', 'MN', 'AZ']```
| Elissa        | ```['NJ', 'WV', 'VA', 'AR', 'WI', 'SD', 'MI', 'NM']```
| Kiran         | ```['NH', 'SC', 'OH', 'NC', 'FL', 'NE', 'WY', 'MT']```
| Kevin         | ```['VT', 'ME', 'PA', 'NY', 'MO', 'KS', 'OR', 'CA']```
| Mariela       | ```['MA', 'IN', 'MS', 'IA', 'OK', 'ID', 'CO', 'TX']```
| Rohan         | ```['HI', 'KY', 'LA', 'IL', 'ND', 'UT', 'NV', 'AK']```

Each person's list is ordered by geographic size. Each state is going to take *a while* to execute. Feel free to
 leave it running in the background while you do other stuff on your computer, **just make sure that your computer
  doesn't fall asleep in the middle of a run.**
  
  Please try and have at least one or two states processed by our next team meeting on Monday, April 27th.
  
 ### Step 6: Run redistrict_state.py
 
 Right click on the redistrict_state.py under [Algorithm(s) To Determine District Lines/redistrict/](<Algorithm(s) To Determine District Lines/redistrict/redistrict_state.py>) and select
  "Run 'redistrict_state'"
  
  And that's it! The file should process all your assigned states and output a .JSON file for each state in your list
  . Please make sure you commit and push those .JSON files to the remote repository. 
  
  > **Note:** The algorithm outputs a lot of stuff to the console when it's running. This is a good thing! Even if
> the output shows up in red, it's not necessarily a bad sign unless the program crashes. In which case, send  a
> message in the Slack so we can help troubleshoot.