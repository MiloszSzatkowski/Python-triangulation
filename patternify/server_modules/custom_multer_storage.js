// Load dependencies
var _ = require('lodash');
var fs = require('fs');
var path = require('path');
var Jimp = require('jimp');
var mkdirp = require('mkdirp');
var concat = require('concat-stream');
var streamifier = require('streamifier');

// Configure UPLOAD_PATH
// process.env.AVATAR_STORAGE contains uploads/avatars
var UPLOAD_PATH = path.resolve(__dirname, './uploads', process.env.AVATAR_STORAGE);

// create a multer storage engine
var Custom_multer_storage = function(options) {

    // this serves as a constructor
    function Custom_multer_storage(opts) {}

    // this creates a Writable stream for a filepath
    Custom_multer_storage.prototype._createOutputStream = function(filepath, cb) {

      var that = this;

      // create a writable stream from the filepath
      var output = fs.createWriteStream(filepath);

      // set callback fn as handler for the error event
      output.on('error', cb);

      // set handler for the finish event
      output.on('finish', function() {
        cb(null, {
          destination: that.uploadPath,
          baseUrl: that.uploadBaseUrl,
          filename: path.basename(filepath),
          storage: that.options.storage
        });
      });

      // return the output stream
      return output;
    };

    Custom_multer_storage.prototype._processImage = function(image, cb) {

      var that = this;

      var batch = [];

      var filename = new Date();

      var mime;

      switch (this.options.output) {
        case 'jpg':
          mime = Jimp.MIME_JPEG;
          break;
        case 'png':
        default:
          mime = Jimp.MIME_PNG;
          break;
      }

      // map through the responsive sizes and push them to the batch
      batch = _.map(sizes, function(size) {

          var outputStream;

          var image = null;
          var filepath = filename.split('.');

          // create the complete filepath and create a writable stream for it
          filepath = filepath[0] + '_' + size + '.' + filepath[1];
          filepath = path.join(that.uploadPath, filepath);
          outputStream = that._createOutputStream(filepath, cb);

          // // scale the image based on the size
          // switch (size) {
          //   case 'sm':
          //     image = clone.clone().scale(0.3);

          image = clone.clone();

          // push an object of the writable stream and Jimp image to the batch
          batch.push({
            stream: that._createOutputStream(path.join(that.uploadPath, filename), cb),
            image: clone
          });

        });

        // process the batch sequence
        _.each(batch, function(current) {
          // get the buffer of the Jimp image using the output mime type
          current.image.getBuffer(mime, function(err, buffer) {
            if (that.options.storage == 'local') {
              // create a read stream from the buffer and pipe it to the output stream
              streamifier.createReadStream(buffer).pipe(current.stream);
            }
          });
        });

      }

      // multer requires this for handling the uploaded file
      Custom_multer_storage.prototype._handleFile = function(req, file, cb) {
        // create a reference for this to use in local functions
        var that = this;

        // create a writable stream using concat-stream that will
        // concatenate all the buffers written to it and pass the
        // complete buffer to a callback fn
        var fileManipulate = concat(function(imageData) {

          // read the image buffer with Jimp
          // it returns a promise
          Jimp.read(imageData)
            .then(function(image) {
              // process the Jimp image buffer
              that._processImage(image, cb);
            })
            .catch(cb);
        });

        // write the uploaded file buffer to the fileManipulate stream
        file.stream.pipe(fileManipulate);
      }

      // multer requires this for destroying file
      Custom_multer_storage.prototype._removeFile = function(req, file, cb) {

        var matches, pathsplit;
        var filename = file.filename;
        var _path = path.join(this.uploadPath, filename);
        var paths = [];

        // delete the file properties
        delete file.filename;
        delete file.destination;
        delete file.baseUrl;
        delete file.storage;

        // create paths for responsive images
        if (this.options.responsive) {
          pathsplit = _path.split('/');
          matches = pathsplit.pop().match(/^(.+?)_.+?\.(.+)$/i);

          if (matches) {
            paths = _.map(['lg', 'md', 'sm'], function(size) {
              return pathsplit.join('/') + '/' + (matches[1] + '_' + size + '.' + matches[2]);
            });
          }
        } else {
          paths = [_path];
        }

        // delete the files from the filesystem
        _.each(paths, function(_path) {
          fs.unlink(_path, cb);
        });


      }

      // create a new instance with the passed options and return it
      return new Custom_multer_storage(options);

    };

    // export the storage engine
    module.exports = Custom_multer_storage;
