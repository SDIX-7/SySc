<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-logo">
        <h2>缺陷检测算法展示平台</h2>
      </div>
      <div class="login-form">
        <el-form :model="loginForm" :rules="loginRules" ref="loginForm" label-position="top">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="loginForm.username" placeholder="请输入用户名" prefix-icon="el-icon-user"></el-input>
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input type="password" v-model="loginForm.password" placeholder="请输入密码" prefix-icon="el-icon-lock" show-password></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="login" round class="login-btn">登录</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data () {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      loginRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    login () {
      this.$refs.loginForm.validate((valid) => {
        if (valid) {
          // 调用登录API
          this.$api.login(this.loginForm).then(res => {
            if (res.success) {
              // 保存用户信息到Vuex
              this.$store.commit('user/SET_USER_INFO', res.data)
              // 跳转到检测页面
              this.$router.push('/Detecting')
            } else {
              this.$message.error(res.message)
            }
          }).catch(err => {
            // 处理错误
            console.error('登录失败:', err)
            this.$message.error('登录失败，请检查用户名和密码')
          })
        }
      })
    }
  }
}
</script>

<style scoped>
.login-container {
  background: url("../assets/home_page_bg.jpg") no-repeat center;
  background-size: 100% 100%;
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.login-container::after {
  z-index: -1;
  position: absolute;
  content: '';
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgb(9, 9, 9);
  opacity: 0.3;
}

.login-box {
  width: 400px;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 10px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
  padding: 30px;
}

.login-logo h2 {
  text-align: center;
  color: #4d86ff;
  margin-bottom: 30px;
  font-size: 24px;
}

.login-form {
  width: 100%;
}

.login-btn {
  width: 100%;
  height: 45px;
  font-size: 16px;
  background-color: #4d86ff;
  border: none;
}

.login-btn:hover {
  background-color: #3a75e0;
}
</style>
