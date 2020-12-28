const gis = require("g-i-s");
const download = require("image-downloader");
const exec = require("child_process").exec;
const path = require('path');
const fs = require('fs');

let sref = null;

function getRandomInt(max) {
  var randNum = Math.floor(Math.random() * Math.floor(max));
  return randNum;
}

async function draw() {
  if (sref == null) {
    let sref_img2bmp = null;
    var img2bmp =
      "convert ./images/output.jpg -negate  -threshold 70% output.bmp";
    sref_img2bmp = exec(img2bmp);
    sref_img2bmp.on("close", (code) => {
      console.log("Finished Img to bmp");
      let sref_svg = null;
      let bmp2svg =
        "potrace --svg output.bmp -t 10 -a 3 -u 10 -P A4 --group -o vect-grib.svg";
      sref_svg = exec(bmp2svg);
      sref_svg.on("close", (code) => {
        console.log("Finished bmp to svg");
        let sref_svgo = null;
        let svgo = "svgo vect-grib.svg";
        sref_svgo = exec(svgo);
        sref_svgo.on("close", (code) => {
          console.log("Finished Svgo");
        });
      });
    });
  }
}


async function logResults(error, results) {
  if (error) {
    console.log(error);
  } else {
    let imgUrl = results[getRandomInt(10)].url;
    console.log(imgUrl);
    //console.log(JSON.stringify(results, null, "  "));
    let options = {
      url: imgUrl,
      dest: "images/output.jpg",
    };
    await download
      .image(options)
      .then(({ filename }) => {
        console.log("Saved to", filename); // saved to /images/output.jpg
      })
      .catch((err) => console.error(err));
    //await draw();
  }
}


var opts = {
  searchTerm: "Ernst Haeckel drawing",
  queryStringAddition: "&filetype:jpg",
};
gis(opts, logResults);