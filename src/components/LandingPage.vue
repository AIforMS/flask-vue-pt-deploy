<template>
  <div id="wrapper">
    <h1>
      nnUNet 在线分割
    </h1>
    <div class="container">
      <div class="section">
        <h3>需要分割的图片</h3>
        <div class="result-container">
          <div class="hint"
               v-if="!uploadSrc">
            Src
          </div>
          <img v-if="uploadSrc"
               :src="uploadSrc"
               alt="">
        </div>
        <form id="upload-file"
              method="post"
              enctype="multipart/form-data">
          <label for="imageUpload"
                 class="btn">
            选择文件
          </label>
          <input type="file"
                 name="file"
                 @change="contentUpload"
                 id="imageUpload"
                 accept=".png, .jpg, .jpeg, .nii, .nii.gz">
        </form>
        <div v-if="uploadSrc">
        <button class="btn"
                @click="clearCanvas">
            <span>清空</span>
        </button>
        </div>
      </div>

      <div class="section-sub">
        <h3>开始分割</h3>
        <button class="btn"
                :disabled="!userContent"
                @click="submitDrawing">
          <span class="submit"></span>
          <span>开始分割</span>
        </button>

        <div class="seg-table">
          <table class="pure-table">
            <caption>指标</caption>
            <tr class="pure-table-odd">
              <th>标签面积</th>
            </tr>
            <tr class="pure-table-odd">
              <td>{{labelArea}}</td>
            </tr>
            <tr class="pure-table-odd">
              <th>标签覆盖率</th>
            </tr>
            <tr class="pure-table-odd">
              <td>{{labelCoverage}}</td>
            </tr>
            <tr class="pure-table-odd">
              <th>假的DICE</th>
            </tr>
            <tr class="pure-table-odd" v-if="diceScore">
              <td>{{diceScore}}</td>
            </tr>
          </table>
        </div>
      </div>

      <div class="section">
        <h3>分割结果</h3>
        <div class="result-container">
          <div class="hint"
               v-if="!resultSrc">
            Seg
          </div>
          <img v-if="resultSrc"
               :src="resultSrc"
               alt="">
        </div>
        <div v-if="resultSrc"
             class="hint">右键图片可以保存到本地</div>
      </div>
    </div>

    <div class="overlay"
         v-if="showWaitModal">
      <div class="half-circle-spinner">
        <div class="circle circle-1"></div>
        <div class="circle circle-2"></div>
      </div>
      <div class="content">
        {{ modalContent }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Vue from "vue";


const axiosStyle =
  process.env.NODE_ENV === "development"
    ? axios.create({ baseURL: "http://localhost:5002" })
    : axios.create({ baseURL: "http://localhost:5002" });

const axiosDtype = axios.create({ baseURL: "http://localhost:5002" })

export default {
  name: "LandingPage",

  components: {
    // DrawingBoard,
    // ImageItem
  },

  data() {
    return {
      msg: "Welcome",
      sessionId: "",
      fileName: "",
      fileType: "",
      uploadSuccess: false,

      labelArea: 2,
      labelCoverage: 0.46,
      diceScore: 1,

      userContent: false,
      userStyle: false,
      userStyleSrc: "",

      highReality: true,
      highQuality: false,

      showStyle: true,
      showToggle: false,
      resultSrc: "",
      uploadSrc: "",

      showWaitModal: false,
      modalContent: "正在分割...",
      submitDisable: true
    };
  },

  mounted: function() {
    this.selectedId = 1;
    this.sessionId =
      "_" +
      Math.random()
        .toString(36)
        .substr(2, 9);

    let that = this;
  },

  methods: {
    clearCanvas() {
      // this.$refs.canvas.clearCanvas();
      this.uploadSrc = '';
      this.resultSrc = '';
    },

    onSelectStyle(id) {
      this.selectedId = id;
      this.submitDisable = false;
    },

    submitDrawing() {
      var container = this.$el.querySelector(".result-container");
      container.scrollIntoView({ behavior: "smooth" });

      // Build form data
      var styleData = new FormData();

      styleData.append("id", this.sessionId);
      styleData.append("fileName", this.fileName);
      styleData.append("fileType", this.fileType);
      if(this.fileType === 'img') {
        styleData.append("contentData", 'img');  // png need to be upload
      } else {
        styleData.append("contentData", 'nii');
      }
      styleData.append("userContent", this.userContent);

      // Use custom image
      if (this.userContent) {
        this.modalContent = "正在分割";
        this.showWaitModal = true;

        axiosStyle({
          url: "/seg",
          method: "POST",
          data: styleData,
          headers: {
            "Content-Type": "multipart/form-data"
          }
        }).then(response => {
          this.showWaitModal = false;
          this.resultStyle = response.data['seg_out'];
          this.resultSrc = this.resultStyle;
          this.labelArea = response.data['labelArea'];
          this.labelCoverage = response.data['labelCoverage'];
          this.diceScore = response.data['fakeDice'];
          this.showToggle = false;
        });
      } else {
        // Use sketch
        this.modalContent = "完蛋了...";
        this.showWaitModal = true;
      }
    },

    contentUpload(e) {
      var files = e.target.files || e.dataTransfer.files;
      if (!files.length) return;
      console.log(files)
      console.log(files[0])

      const imgList = ['png', 'jpg', 'jpeg']
      const niiList = ['nii', 'nii.gz', 'gz']

      var fileName = files[0]['name']
      var fileArr = fileName.split('.')
      var fileEnds = fileArr[fileArr.length - 1].toLocaleLowerCase()
      if(imgList.find(item => item  === fileEnds)) {
        this.fileType = 'img'
      } else {
        this.fileType = 'nii'
      }
      this.fileName = fileArr[0]
      
      console.log(this.fileName)
      console.log(this.fileType)

      var reader = new FileReader();
      var uploadData = new FormData()

      uploadData.append("file", files[0])
      uploadData.append("fileName", this.fileName)
      uploadData.append("fileType", this.fileType)
      uploadData.append("id", this.sessionId)

      if(this.fileType === 'img') {
        reader.onload = e => {
          this.uploadSrc = e.target.result;  // 前端处理的图片的base64编码
        };
        reader.readAsDataURL(files[0]);  // base64编码
        e.target.value = "";
        axiosDtype({
          url: "/uploader",
          method: "POST",
          data: uploadData,
          headers: {
            "Content-Type": "multipart/form-data"
          }
          }).then(response => {
            this.uploadSuccess = true
          });
      } else {
        axiosDtype({
          url: "/uploader",
          method: "POST",
          data: uploadData,
          headers: {
            "Content-Type": "multipart/form-data"
          }
        }).then(response => {
          this.uploadSrc = response.data;  // 后端上传的图片的 base64 编码
          this.uploadSuccess = true
          // this.resultSrc = this.resultStyle;
        });
      }
      this.userContent = true;
    },

    setUserStyleSrc(data) {
      this.userStyleSrc = data;
      this.userStyle = true;
      this.submitDisable = false;

      var submit = this.$el.querySelector(".submit");
      submit.scrollIntoView({ behavior: "smooth" });
    },
  }
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#wrapper h1 {
  margin: 1rem 0rem;
}

#wrapper h3 {
  margin-top: 0.2rem;
  margin-bottom: 0.8rem;
}

.container {
  display: flex;
}

.section {
  margin: 0.5rem 1rem;
  flex-grow: 1;
  width: 40%;
}

.section .options .vue-js-switch {
  margin: 0.5rem;
}

.section-sub {
  margin: 0.5rem 0.5rem;
  flex-grow: 1;
  width: 15%
}

.seg-table {
  display: flex;
  justify-content: center;
}

.image-container .image-flex {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  max-width: 400px;
  margin: 0 auto;
}

.image-container .image-item {
  width: 25%;
  margin: 3px;
  padding: 2px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.055);
  transition: all 0.2s ease-in-out;
}

.image-container .image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  overflow: hidden;
}

img.selected {
  box-sizing: border-box;
  border: 4px solid #0088cc;
}

.result-container {
  margin: 0 auto;
  max-width: 400px;
  min-height: 420px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #ffffff;
  padding: 0.5rem;
  display: flex;
  justify-content: center;
  align-items: center;
}

.result-container img {
  border: 1px solid #eee;
  border-radius: 0.2rem;
  width: 100%;
  height: 100%;
  object-fit: cover;
  overflow: hidden;
}

.hint {
  font-weight: 200;
  font-size: 1rem;
  color: #95a5a6;
}

.overlay {
  position: fixed;
  z-index: 9998;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  color: #bdc3c7;
}

.overlay .content {
  margin: 1rem;
}

@media only screen and (max-width: 800px) {
  .container {
    /* display: flex; */
    flex-direction: column;
  }

  .section {
    margin: 0;
    width: 100%;
  }

  .canvas-wrapper {
    max-height: 500px;
  }
}

.canvas-wrapper {
  max-height: 500px;
  height: auto;
  padding: 10px;
}

.btn {
  background-color: #008cba;
  border: none;
  border-radius: 0.3em;
  color: white;
  padding: 0.5em 1em;
  margin: 0.5em;
  font-size: 1rem;
  font-family: inherit;
  font-weight: 400;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  -webkit-transition-duration: 0.4s; /* Safari */
  transition-duration: 0.4s;
  cursor: pointer;
}

.btn:hover {
  background: #34495e;
}

.btn.disabled,
.btn[disabled],
fieldset[disabled] .btn {
  pointer-events: none;
  cursor: not-allowed;
  box-shadow: none;
  opacity: 0.5;
}

input[type="file"] {
  display: none;
}

.style-hint form {
  display: inline;
}

.style-hint {
  font-weight: 200;
  font-size: 0.8rem;
  color: #95a5a6;
}

.style-hint .upload-label {
  text-decoration: underline;
}

.upload-label {
  cursor: pointer;
  font-weight: 200;
  font-size: 0.8rem;
  color: #95a5a6;
}

.upload-style img {
  width: 120px;
  height: 120px;
  margin: 0.2rem;
  padding: 2px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.055);
  transition: all 0.2s ease-in-out;
}

.upload-style .remove {
  cursor: pointer;
  font-weight: 200;
  font-size: 0.8rem;
  color: #95a5a6;
  text-decoration: underline;
}

span.clear {
  background: url("../assets/icons/eraser.svg") no-repeat top left;
  background-size: contain;
  cursor: pointer;
  display: inline-block;
  height: 1rem;
  width: 1rem;
}

span.submit {
  background: url("../assets/icons/palette.svg") no-repeat top left;
  background-size: contain;
  cursor: pointer;
  display: inline-block;
  height: 1rem;
  width: 1rem;
}

span.upload {
  background: url("../assets/icons/upload.svg") no-repeat top left;
  background-size: contain;
  cursor: pointer;
  display: inline-block;
  height: 1rem;
  width: 1rem;
}

.half-circle-spinner,
.half-circle-spinner * {
  box-sizing: border-box;
}

.half-circle-spinner {
  width: 4rem;
  height: 4rem;
  border-radius: 100%;
  position: relative;
}

.half-circle-spinner .circle {
  content: "";
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 100%;
  border: calc(60px / 10) solid transparent;
}

.half-circle-spinner .circle.circle-1 {
  border-top-color: #bdc3c7;
  animation: half-circle-spinner-animation 1s infinite;
}

.half-circle-spinner .circle.circle-2 {
  border-bottom-color: #bdc3c7;
  animation: half-circle-spinner-animation 1s infinite alternate;
}

table {
    margin: 2em;
    border-collapse: collapse;
    border-spacing: 0;
}

td,th {
    padding: 0;
}

.pure-table {
    border-collapse: collapse;
    border-spacing: 0;
    empty-cells: show;
    border: 1px solid #cbcbcb;
}

.pure-table caption {
    color: #000;
    font-weight: 600;
    font-size: 1em;
    margin-bottom: 0.5em;
    text-align: center;
}

.pure-table td,.pure-table th {
    border-left: 1px solid #cbcbcb;
    border-width: 0 0 0 1px;
    font-size: inherit;
    margin: 0;
    overflow: visible;
    padding: .5em 1em;
}

.pure-table thead {
    background-color: #008cba;
    color: #000;
    text-align: left;
    vertical-align: bottom;
}

.pure-table td {
    background-color: transparent;
}

.pure-table-odd td {
    background-color: #ffffff;
}

@keyframes half-circle-spinner-animation {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
