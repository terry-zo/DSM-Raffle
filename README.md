# DSM-Raffle
## Run using python 2.7

Enters DSM Raffle with captcha requests from 2captcha.

## Instructions

  * First, you must enter all appropriate information in **config.json**.
    * **email** is the email you want all your entries under. Please refer to **E-Mail**.
    * **fullname** is your first and last name.
    * **2captcha-api** is the api key for your [2captcha](https://goo.gl/T1c75n) account.
    * **raffle-sitekey** is the captcha identifier for [DSM](https://www.doverstreetmarket.com/). The sitekey is pre-filled, and should only be changed if [DSM](https://www.doverstreetmarket.com/) renewed their sitekey.
    * **how-many-times-do-you-want-to-enter-the-raffle** is how many times you want to enter the raffle.
    * **proxyfile** is the name of the file your proxies are in.
  * Secondly, you must install the modules required for the script to work. Please refer to **Required modules**.

**_Note_** If you don't have a 2captcha account, you can create one [here](https://goo.gl/T1c75n).

## Proxies
_Proxies implemented 5-8-18_

  * Every proxy must be on its own line.
  * Every proxy must be the following format:

    * Supports IP Authentication proxies:
    ```ip:host```

    * Supports user:pass Authentication proxies:
    ```ip:host:user:pass```


  * **Example**:
  ```
  123.123.123.123:12345:hello:bye
  123.123.123.123:12345:hello:bye
  123.123.123.123:12345:hello:bye
  123.123.123.123:12345:hello:bye
  123.123.123.123:12345
  123.123.123.123:12345
  123.123.123.123:12345
  123.123.123.123:12345
  ```

## E-Mail
_Catch-all implemented 5-9-18_

  * **email** in **config.json** must be the following format:
  ```
  zoegodterry@gmail.com
  @zoegodterry.club
  ```

## Required modules

Before running the script, the following modules are required:
```requests names```

This can be accomplished by running the following command in a command prompt:

```
pip install requests names
```

## Other scripts

I _might or might not_ release more scripts on my [twitter](https://twitter.com/zoegodterry).

Follow to be the **first ones to know**!
