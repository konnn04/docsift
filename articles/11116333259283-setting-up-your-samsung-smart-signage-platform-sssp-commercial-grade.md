# Setting Up Your Samsung Smart Signage Platform (SSSP - Commercial Grade)

Article URL: https://support.optisigns.com/hc/en-us/articles/11116333259283-Setting-Up-Your-Samsung-Smart-Signage-Platform-SSSP-Commercial-Grade
Section: Use Your Players
Last Updated: 2026-06-10T11:03:57Z

---

### Samsung Smart Signage Platform —SSSP— powered displays are one of the most popular commercial grade TVs. OptiSigns supports Samsung SSP devices natively. Nearly all features are supported, including offline playback and auto update of the OptiSigns app. Getting your SSSP with OptiSigns is an easy process!

|  |
| --- |
| **This article is for installing OptiSigns on Samsung SSP devices only!** |
| Your screen should be marked as "SSSP/Samsung Smart Signage Platform". Samsung has other product lines that run on Tizen OS, and aren't SSSPs. Not sure if your Samsung Smart TV is an SSP or uses Tizen OS? Check out our [**Full List of Samsung SSP Models.**](https://support.optisigns.com/hc/en-us/articles/17882306279315-Samsung-Smart-Signage-Platform-SSSP-Supported-Model-List) |

*\*For TVs utilizing Samsung Tizen OS, please use this guide:* [*How to use OptiSigns with Browser*](https://www.optisigns.com/post/how-to-use-optisigns-with-browser)*.*

---

### In this article:

- [OptiSigns Installation Process:](#Installation)
  - [Option 1: Install on an SSSP Display That is Already in Use](#1)
  - [Option 2: Install on a Brand New SSSP Display Through Out of Box Experience Setup](#2)
- [Limitations](#Limitations)

---

## OptiSigns Installation Process

The installation process to get OptiSigns on your SSSP is easy! There are two different scenarios for you:

- **Install on a SSSP display that is already in use:** You already have SSSP display in use and would like to have OptiSigns player for SSSP deployed.
- **Install on a brand new SSSP display through out of box experience setup:** You have a brand new SSSP display or you just performed a factory reset. You can connect to OptiSigns through the out of box experience/initial set-up process.

*For a detailed visual guide for these options, please watch and follow along with our SSSP installation instructional video:*

---

## Option 1: Install on an SSSP Display That is Already in Use:

*First, ensure your screen is connected to the internet before proceeding.*

Press the **"Home"** button on the remote to begin.

|  |  |
| --- | --- |
| **Current/New Models** | **Older Models** |
| Select: **App Management** | Select: **URL Launcher Settings** |
|  |  |
| Your App Management/URL Launcher Settings will open. If you already have an app installed, select: **Uninstall**. Proceed once there are no apps installed. | |
| Select: **Install Custom App** | Select: **Install Web App** |
| Enter in the URL of the OptiSigns app for SSSP: **https://t.optisigns.com** | |
| Select: **Go** | Select: **Done** |

The OptiSigns app will automatically begin to download.

The OptiSigns app for SSSP is now installed and will automatically launch, showing a pairing code on your device:

Now, you are ready to pair the screen and begin assigning content to it. After you pair your screen, the OptiSigns app will automatically launch each time the SSSP screen is turned on.

*For detailed steps on pairing your screen and publishing content, see our simple* [*set up & add screen guide*](https://support.optisigns.com/hc/en-us/articles/360016374813-Set-up-add-a-screen)*.*

---

## Option 2: Install on a Brand New SSSP Display Through Out-of-Box Experience Setup:

This option is if your SSSP display is new, or just went through a factory reset. It will start with the out-of-box experience to guide you through the initial setup.

Please note:

- Older models go through the same steps, but in a different order.
- If you are not automatically moved to the next prompt, simply click the right arrow button on your remote, and select "Next", found in the top right of the screen.

|  |  |
| --- | --- |
| **Current/New Models** | **Older Models** |
| Select your **Language**. | Select your **Language**. |
| Connect to your desired internet network. | Installation Type, select: **Basic Setup** |
| Smart Signage Privacy Notice, select: **OK** | Select the proper Display Orientation. **Do not skip this step.** You will not be able to change this setting remotely through OptiSigns. You can only change it through your screen settings on-site with the TV remote. |
| Installation Type, select: **Basic Setup** | Connect to your desired internet network. |
| Select the proper Display Orientation. **Do not skip this step.** You will not be able to change this setting remotely through OptiSigns. You can only change it through your screen settings on-site with the TV remote. | Smart Signage Privacy Notice, select: **OK** |
| Player Selection, select: **Custom App** | Play via select: **URL Launcher** |
| Enter the OptiSigns app URL: **https://t.optisigns.com** and select: **Go** | Enter the OptiSigns app URL: **https://t.optisigns.com** and select: **Done** |
| Connect to RM Server, select: **Skip** | Connect to RM Server, select: **Skip** |
| **Do not skip this**, and be sure to enter the correct Date & Time. If you skip, or enter incorrectly, your SSSP screen will not connect to the OptiSigns app. | |
| Set Current Time | Clock Set |
| **Set PIN**. *Creating a PIN is optional.* Enter a new PIN, or leave blank, and select: **Next** | Depending on the software version of your older model, you may be prompted to set a PIN. Our testing screen does not prompt us to set a PIN. If you are prompted too, then simply create a PIN or skip that step. |
| Set-up Process is complete. | Select "**Done**" to complete the set-up process. |
| A menu will automatically appear at the bottom of your screen. If it does not, simply press the "**Home**" button your remote. | |
| Select "**Custom** App" to launch OptiSigns. | Select **"URL Launcher**" to launch OptiSigns. |

The OptiSigns app will open and a pairing code will appear:

Now you are ready to pair the screen and begin assigning content to it. After you pair your screen, the OptiSigns app will automatically launch each time the SSSP screen is turned on.

For detailed steps on pairing your screen and publishing content, see our simple [set up & add screen guide](https://support.optisigns.com/hc/en-us/articles/360016374813-Set-up-add-a-screen).

---

## Limitations

Samsung SSP graphics resolution output is 1080P only. Take precaution when using 4k videos. Samsung SSP can only process a single video at any point of time. Preloading of the next video is not allowed. The transition from video to video is not as smooth as other players that allow video preloading.

#### SSSP 10 (Tizen 6.5)

The "Seamless Video Playback" feature released for these models can cause screen glitches. Seamless playback is meant to play videos back-to-back without the screen ever going black in between.

Here are a few known workarounds:

- Keep all videos encoded in h264, but ensure the resolution for all videos are the same.
  - In other words, don't switch between HD (1980x1080) and 4K (3840x2160) videos.
- Re-encode all videos to h265 (we recommend [**Handbrake**](https://handbrake.fr/)for this). This way, all the videos can keep their resolution.

---

### That's it! Now you are ready to use OptiSigns on your Samsung SSSP displays.

OptiSigns is a leader in [digital signage software](https://www.optisigns.com/). If you have questions or need additional help, please contact us at [support@optisigns.com.](mailto:support@optisigns.com)
