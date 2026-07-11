# How to display content inside websites that require login?

Article URL: https://support.optisigns.com/hc/en-us/articles/360037391854-How-to-display-content-inside-websites-that-require-login
Section: Web Scripting & Secured Dashboard
Last Updated: 2026-06-25T12:33:44Z

---

Sometimes you have content behind a website that requires log-in, such as your project schedule in Atlassian's JIRA, Trello, dashboard behind Tableau, Salesforces, etc.

It can either be a Browser Popup or a Gated Website (like below)

The solution is simple, you just need to:

- Copy the link to the page, and dashboard you need to display.
- Put it in the Website app in OptiSigns
- Then put the asset on your screen or in the playlist as an asset
- When it shows up on your device, just use your mouse & keyboard to enter in username and password (remember to save credentials, for Fire TV, you may need a [Bluetooth mouse & keyboard](https://www.amazon.com/Logitech-Illuminated-Living-Room-Keyboard-Touchpad/dp/B00ZOPVSKW/) to pair and type this information in).
- If you don't have a Bluetooth mouse & keyboard, you can use a [USB HUB adaptor](https://support.optisigns.com/hc/en-us/articles/360055080914) to connect with your mouse & keyboard.

That's it, the credential will be saved, and every time OptiSigns plays the link, it will show the secured information inside the website.

Enter the Website URL:

Note: Browser Popup kind of password is not supported for Android, FireStick player. Only Windows, Linux, MacOS, Raspberry Pi, and ChromeOS are supported. The app will pop up a window for you to enter password:

You can also prefill a password in your URL for the Browser Popup case such as: <https://guest:guest@jigsaw.w3.org/HTTP/Basic/>
