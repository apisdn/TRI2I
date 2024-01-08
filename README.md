# TRI2I: TIR RGB Image-to-Image Translation
## Dataset
The dataset consists of 148,829 TIR/RGB image pairs collected in 16-20k capture sessions in and around Salt Lake City, Utah. It includes a variety of global priors in both lighting and situation, as summarized in the table below. The dataset is available for download [here](https://drive.google.com/file/d/1qorMXaQa57tq8Nj3dFBd-s0oU42tWbC0/view?usp=drive_link)

| Data Range    | Location    | Time of Day   | Weather       | Time of Year |
| :---          |    :----:   |         :---: |         :---: | ----:        |
| 1443-16021    | Campus      | Day           | Overcast      | Spring       |
| 16022-33789   | Suburban    | Early Dusk    | Overcast      | Spring       |
| 33798-51820   | Suburban    | Day           | Clear         | Winter       |
| 52748-71268   | Urban       | Day           | Clear/Cloudy  | Spring       |
| 71316-93615   | Suburban    | Late Dusk     | Clear         | Summer       |
| 93616-124344  | Urban       | Night         | Clear         | Summer       |
| 124345-151373 | Suburban    | Night         | Clear         | Fall         |

This dataset is as wide ranging as was possible given the imaging system and location, however we do acknowledge its limitations. For example, it was not possible to image in adverse weather conditions such as snow or rain.

## Example Results
Example results from training the dataset for Image to Image (I2I) translation are available in the 'example_results folders'. Details about the training process are available in the paper.
## Utilities
Some code and scripts used to capture, divide, and analyze data during this project is available in the utils folder. Code for the models used was taken from the original pix2pix creators, and is available [on their page](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix).
