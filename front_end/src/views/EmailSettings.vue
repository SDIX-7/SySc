<template>
  <div class="container">
    <Menu></Menu>
    <div class="title">
      <span>邮箱设置</span>
    </div>
    <div class="email-settings-content">
      <div class="content-wrapper">
        <el-card class="email-settings-card">
          <div class="email-settings-form">
            <h3>控制图报警邮箱设置</h3>
            <p class="email-description">设置控制图异常时接收报警邮件的邮箱地址</p>
            <el-form :model="emailForm" :rules="emailRules" ref="emailForm" label-width="150px">
              <el-form-item label="当前报警邮箱">
                <el-input v-model="emailForm.currentEmail" disabled placeholder="暂无设置"></el-input>
              </el-form-item>
              <el-form-item label="新邮箱地址" prop="newEmail">
                <el-input v-model="emailForm.newEmail" placeholder="请输入新邮箱地址" prefix-icon="el-icon-message"></el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveEmail" round>保存设置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script>
import Menu from '../components/Menu.vue'
import { getEmailSettings, saveEmailSettings } from '../api/api'

export default {
  name: 'EmailSettings',
  components: {
    Menu
  },
  data () {
    return {
      emailForm: {
        currentEmail: '', // 当前邮箱地址
        newEmail: '' // 新邮箱地址
      },
      emailRules: {
        newEmail: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
        ]
      }
    }
  },
  mounted () {
    // 从后端获取当前邮箱地址
    this.getEmailSettings()
  },
  methods: {
    // 获取邮箱设置
    async getEmailSettings () {
      try {
        // 调用API获取当前邮箱设置
        const response = await getEmailSettings()
        if (response && response.data) {
          this.emailForm.currentEmail = response.data.email || ''
        }
      } catch (error) {
        console.error('获取邮箱设置失败:', error)
        this.$message.error('获取邮箱设置失败')
      }
    },
    // 保存邮箱设置
    async saveEmail () {
      this.$refs.emailForm.validate(async (valid) => {
        if (valid) {
          try {
            // 调用API保存邮箱设置
            await saveEmailSettings({ email: this.emailForm.newEmail })
            // 更新当前邮箱显示
            this.emailForm.currentEmail = this.emailForm.newEmail
            this.emailForm.newEmail = ''
            this.$message.success('邮箱设置保存成功')
          } catch (error) {
            console.error('保存邮箱设置失败:', error)
            this.$message.error('保存邮箱设置失败')
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.container {
  background: url("../assets/bg5.jpg") no-repeat center;
  background-size: 100% 100%;
  min-height: 100vh;
  position: relative;
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

.title {
  margin-top: 1%;
  font-size: 3vw;
  color: #5485c2;
  margin-left: 50px;
}

.title span {
  letter-spacing: 1vw;
}

.email-settings-content {
  margin-top: 20px;
  padding: 0 50px;
}

.content-wrapper {
  background-color: rgba(255, 255, 255, 0.9);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center;
}

.email-settings-card {
  max-width: 600px;
  width: 100%;
}

.email-settings-form {
  padding: 20px 0;
}

.email-settings-form h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.email-description {
  color: #666;
  margin-bottom: 30px;
}

.email-settings-form .el-button {
  margin-top: 20px;
}
</style>
