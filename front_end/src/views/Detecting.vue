<template>
  <div class="container">
    <!-- <div class="logo">
      <img src="../assets/CJLUlogo.jpg" alt=""/>
    </div> -->
    <Menu></Menu>
    <div class="title">
      <span>请选择您想要的功能</span>
    </div>
    <div class="content">
      <el-button class="button1" type="info" circle @click="detectByImg">
        <div class="btn-icon">
          <i class="el-icon-camera"></i>
        </div>
        <div class="btn-title">
          <span>图像检测</span>
        </div>
        <div class="btn-content">
          <p>可上传本地文件中的图像进行检测</p>
          <p>支持jpg, png, jpeg等图像格式</p>
        </div>
      </el-button>
      <el-button class="button2" type="info" circle @click="History">
        <div class="btn-icon">
          <i class="el-icon-document"></i>
        </div>
        <div class="btn-title">
          <span>历史记录</span>
        </div>
        <div class="btn-content">
          <p>对检测过的图像进行查看</p>
          <p>返回检测结果</p>
        </div>
      </el-button>
      <el-button class="button3" type="info" circle @click="ProcessControl">
        <div class="btn-icon">
          <i class="el-icon-data-line"></i>
        </div>
        <div class="btn-title">
          <span>过程控制</span>
        </div>
        <div class="btn-content">
          <p>质量控制图分析</p>
          <p>过程能力评估</p>
        </div>
      </el-button>
      <el-button class="button4" type="info" circle @click="EmailSettings">
        <div class="btn-icon">
          <i class="el-icon-message"></i>
        </div>
        <div class="btn-title">
          <span>邮箱设置</span>
        </div>
        <div class="btn-content">
          <p>设置控制图报警邮箱</p>
          <p>接收异常检测报警通知</p>
        </div>
      </el-button>
      <el-button class="button5" type="info" circle @click="UserManagement">
        <div class="btn-icon">
          <i class="el-icon-user"></i>
        </div>
        <div class="btn-title">
          <span>人员管理</span>
        </div>
        <div class="btn-content">
          <p>管理系统用户</p>
          <p>添加或删除用户</p>
        </div>
      </el-button>
    </div>
  </div>
</template>

<script>
import Menu from '../components/Menu.vue'
export default {
  name: 'Detecting',
  components: {
    Menu
  },
  data () {
    return {}
  },
  methods: {
    // 图片检测
    detectByImg () {
      this.$router.push({path: '/DetectByImg'})
      console.log('图像检测')
    },
    // 历史记录
    History () {
      this.$router.push({path: '/History'})
      console.log('历史记录')
    },
    // 过程控制
    ProcessControl () {
      this.$router.push({path: '/ProcessControl'})
      console.log('过程控制')
    },
    // 邮箱设置
    EmailSettings () {
      this.$router.push({path: '/EmailSettings'})
      console.log('邮箱设置')
    },
    // 人员管理
    UserManagement () {
      this.$router.push({path: '/UserManagement'})
      console.log('人员管理')
    }
  }
}
</script>

<style scoped>
.container {
  background: url("../assets/bg5.jpg") no-repeat center;
  background-size: 100% 100%;
}

.container::after {
  z-index: -1;
  position: absolute;
  content: '';
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.51);
  opacity: 0.3;
}

.logo {
  margin-left: 3%;
  padding-top: 3%;
  width: 8%;
}

.logo img {
  width: 100%;
}

.title {
  margin-top: 1%;
  font-size: 3vw;
  color: #5485c2;
  margin-left: 50px;
}

.title span {
  letter-spacing: 1vw;
}

.content {
  margin-top: 1%;
}

.content button {
  position: relative;
  width: 16%;
  height: 60vh;
  border-radius: 40px;
  transition: all 0.4s;
  margin: 1% 1%;
  /* text-align: center; */
}

.button1{
  background: url("../assets/but1.jpg");
  background-size: 288px 592px;
}

.button2{
  background: url("../assets/but2.jpg");
  background-size: 288px 592px;
}

.button3{
  background: url("../assets/but3.jpg");
  background-size: 288px 592px;
}
.button4{
  background: url("../assets/but1.jpg");
  background-size: 288px 592px;
}
.button5{
  background: url("../assets/but2.jpg");
  background-size: 288px 592px;
}
.content button:hover {
  width: 18%;
  height: 65vh;
  margin: 0 1%;
  transition: all 0.4s;
}

.content .btn-icon {
  width: 100%;
  position: absolute;
  top: 15%;
  left: 0;
  height: 10%;
  font-size: 4.5vh;
}
.content .btn-title {
  width: 100%;
  position: absolute;
  top: 40%;
  left: 0;
  height: 15%;
  font-size: 3.5vh;
}

.content .btn-title span {
  letter-spacing: .5vw;
}

.content .btn-content {
  width: 100%;
  position: absolute;
  top: 55%;
  left: 0;
  font-size: 2vh;
}

.content .btn-content p{
  margin-top: 5%;
}
</style>
