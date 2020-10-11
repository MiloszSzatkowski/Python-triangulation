<template>
<div class="file_upload_container">
  <form @submit.prevent="onSubmit" id="triangulation_form" class="" enctype="multipart/form-data">
    <div class="fields">
      <label for="myfile">Select a file:</label>
      <br>
      <input type="file" id="myfile" name="myfile"
      ref="file"
      @change="onSelect" accept=".jpg,.jpeg,.png" required>
    </div>
    <div class="fields">
      <input type="submit" name="" value="">
    </div>
    <div class="message">
      <h5>{{message}}</h5>
    </div>
  </form>
</div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Triangulation',
  data() {
    return {
      file: "",
      message: ""
    }
  },
  methods: {
    onSelect() {
      this.message = '';
      console.log('you\'ve selected a file');
      const allowedTypes = ["image/jpeg", "image/jpg", "image/png"];
      const file = this.$refs.file.files[0];
      this.file = file;
      if (!allowedTypes.includes(file.type)) {
        this.message = "Filetype is wrong!!"
      }
      if (file.size > 1000000) {
        this.message = 'Too large, max size allowed is 1000kb'
      }
    },
    async onSubmit() {
      console.log('submition in progress');
      const formData = new FormData();
      formData.append('file', this.file);
      try {
        await axios.post('http://localhost:5000/upload', formData);
        this.message = 'Uploaded';
      } catch (err) {
        console.log(err);
        this.message = err.response.data.error
      }
    }
  },
}
</script>
