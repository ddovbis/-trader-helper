REQUIREMENTS
1. Python 3.7
2. Internet connection
3. Alpha Vantage (AV) API key

TESTED ON:
- OS: Microsoft Windows 10 Pro, v. 21H2 (OS Build 19044.1645)
- Hardware:
    - Processor: Intel(R) Core(TM) i7-1065G7 CPU @ 1.30GHz, 1501 Mhz, 4 Core(s), 8 Logical Processor(s)
    - Installed Physical Memory (RAM):	16.0 GB
- Python version: 3.8.4

INSTALLATION
1. Install TA_Lib v. 0.4.24
    1.1. Try installing it via pip
        pip install TA_Lib==0.4.24
    1.2. If the process ended up in an error related to C Language, and you cannot troubleshoot it, the alternative is to install the wheel manually from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

2. Install modules listed in requirements.txt
    pip install -r requirements.txt

3. Create AV API key (skip this step if you already have one)
    3.1. Go to https://www.alphavantage.co/support/#api-key
    3.2. Fill in the input in the "Claim your Free API Key" section (profession, organization, email, "I'm not a robot" checkbox)
    3.3. Click "GET FREE API KEY"
    3.4. The key should be sent to the introduced email immediately

4. Replace dummy value of "ALPHA_VANTAGE_API_KEY" with your actual key; the config file for this is located in:
    resources/config.py

USAGE:
1. Start the program with "-h" argument to see usage description and examples
    python ./src/app.py

DISCLAIMERS:
- Requirements file has been built with the help of `pipreqs`;
- Minimum Python version detected with `vermin`;
- As of April 28th 2022 — creation of AV API key is completely free, and allows sending up to 5 requests per minute, or 500 requests per day. If any of these limits is reached trader-helper will wait for some time and retry the request.
- trader-helper team is not affiliated in any way with AV, neither is it involved in any referral program with it.
