const express = require ('express');
const cors = require ('cors');
const multer = require('multer');
const path = require('path');
const {spawn} = require('child_process');

const fileSize_max = 1000000;

const app = express();
app.use(cors());


fileFilter = (req, file, cb) => {
  if (file.mimetype == "image/png" || file.mimetype == "image/jpg" || file.mimetype == "image/jpeg") {
     cb(null, true);
   } else {
     const error = new Error ("Incorrect File Extension. Only jpeg, jpg and png files are accepted.");
     error.code = "INCORRECT_FILETYPE";
     return cb(error, false);
   }
};

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
  cb(null, './uploads')
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + '-' +
    file.originalname.toString().replace(/\.[^.]*$/, '') +
    path.extname(file.originalname))
    //Appending extension
  }
});

const upload = multer({
  dest: './uploads',
  fileFilter,
  limits: {
    fileSize: fileSize_max
  },
  storage: storage
});

const PORT = 5000 || process.env.PORT;

app.post('/upload', upload.single('file'), (req,res) => {
  res.json({file: req.file});
});

app.use((err, req, res, next) => {
  if (err.code === "INCORRECT_FILETYPE"){
    res.status(422).json({error: 'Only images are allowed' });
    return;
  }
  if (err.code === "LIMIT_FILE_SIZE"){
    res.status(422).json({error: `Allowed size is ${fileSize_max} kb.` });
    return;
  }
});

app.listen(PORT, () => console.log(`Server listening on port ${PORT}`));

function checkFileType(file, cb){
  // Allowed ext
  const filetypes = /jpeg|jpg|png|gif/;
  // Check ext
  const extname = filetypes.test(path.extname(file.originalname).toLowerCase());
  // Check mime
  const mimetype = filetypes.test(file.mimetype);

  if(mimetype && extname){
    return cb(null,true);
  } else {
    cb('Error: Images Only!');
  }
}
