# Quote

This command cog provides the simple `/where <text>` command, which returns a random meme template with the text added
to it. This is basically a meme template cog, but is called `where` due to it being used for memes
like ["where banana"](https://knowyourmeme.com/memes/where-banana).

## Installation

In the `assets/where` folder, you should add the following:

* An `img` folder containing the template images
* A `font` folder containing true type fonts (`.ttf`)
* A `metadata.json` file containing image information

An example of how a `metadata.json` should be formatted for a single image:

```json
[
  {
    "image": "monke.jpg",
    "prefix": "where ",
    "suffix": "",
    "top_left_box": [
      461,
      22
    ],
    "bottom_right_box": [
      717,
      65
    ],
    "color": "#000000",
    "style": "lowercase"
  }
]
```

Since the assets are bind mounted, a reload of this cog will add new images without taking the bot down. This cog can
also be dynamically enabled if the appropriate libraries are installed.