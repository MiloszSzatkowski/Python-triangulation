const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
var fs = require('fs');

const {
  spawn
} = require('child_process');

const fileSize_max = 1000000;

const app = express();
app.use(cors());


fileFilter = (req, file, cb) => {
  if (file.mimetype == "image/png" || file.mimetype == "image/jpg" || file.mimetype == "image/jpeg") {
    cb(null, true);
  } else {
    const error = new Error("Incorrect File Extension. Only jpeg, jpg and png files are accepted.");
    error.code = "INCORRECT_FILETYPE";
    return cb(error, false);
  }
};

var storage = multer.diskStorage({
  destination: function(req, file, cb) {
    cb(null, './python_code')
  },
  filename: function(req, file, cb) {
    cb(null, Date.now() + '-' +
      file.originalname.toString().replace(/\.[^.]*$/, '') +
      path.extname(file.originalname))
    //Appending extension
  }
});

const upload = multer({
  dest: './python_code',
  fileFilter,
  limits: {
    fileSize: fileSize_max
  },
  storage: storage
});


const PORT = 5000 || process.env.PORT;

app.post('/upload', upload.single('file'), async (req, res) => {

        res.json({
          file: req.file
        });

        try {

          let file_path_name = await path.dirname(require.main.filename) + "\\upload\\" + res.req.file.filename;

          // console.log(file_path_name);

          const python = spawn('python', [(path.dirname(require.main.filename) + '\\python_code\\' + 'triangulation.py'), res.req.file.filename ]);

          // var python_output = '';

          python.stdout.on('data', function(data) {
            console.log('Pipe data from python script ...');
            dataToSend = data.toString();
            // console.log(dataToSend);
            // python_output += dataToSend;
          });

          python.stderr.on('data', function(data) {
            console.error(`stderr: ${data}`);
            err = data.toString();
            console.log('Error: \n' + err);
          });

          // in close event we are sure that stream from child process is closed
          python.on('close', (code) => {
              console.log(`child process close all stdio with code ${code}`);
              //save a buffer with nodejs finish
              // fs.writeFile('new_file.jpg', Buffer.from(python_output), function () { });

              // send data to browser
              // res.send(dataToSend)

            });

          } catch (e) {
            console.log(e);
          }

});

app.use((err, req, res, next) => {
  switch (err.code) {
    case "INCORRECT_FILETYPE":
      res.status(422).json({
        error: 'Only images are allowed'
      });
      return;
      break;
    case "LIMIT_FILE_SIZE":
      res.status(422).json({
        error: `Allowed size is ${fileSize_max} kb.`
      });
      return;
      break;
    default:
  };
});

app.listen(PORT, () => console.log(`Server listening on port ${PORT}`));
