<template>
  <div>
    <el-menu
      :default-active="$route.path"
      class="el-menu-demo"
      mode="horizontal"
      router>
      <img class="logo" src="../assets/CJLUlogo.jpg" alt=""/>
      <el-menu-item v-for="page in dynamicPages"
                    :key="page.index"
                    :index="page.index">
        {{ page.name }}
      </el-menu-item>
      <el-menu-item class="user-info-item" disabled v-if="isLoggedIn">
        当前身份：{{ userRoleText }}
      </el-menu-item>
      <el-menu-item index="/logout" @click="logout" v-if="isLoggedIn">
        退出登录
      </el-menu-item>
    </el-menu>
  </div>
</template>
<script>
import { mapGetters } from 'vuex'

export default {
  name: 'Menu',
  computed: {
    ...mapGetters('user', ['isLoggedIn', 'hasPermission', 'getUserInfo', 'getUserRole']),
    // 动态菜单项
    dynamicPages () {
      let pages = []

      // 检测员、监测员、管理员都显示的菜单项
      pages.push(
        {name: '功能介绍', index: '/Detecting', permission: 'detect'},
        {name: '图像检测', index: '/DetectByImg', permission: 'detect'}
      )

      // 监测员和管理员显示的菜单项
      if (this.hasPermission('history')) {
        pages.push(
          {name: '历史记录', index: '/History', permission: 'history'},
          {name: '过程控制', index: '/ProcessControl', permission: 'process'},
          {name: '邮箱设置', index: '/EmailSettings', permission: 'email'}
        )
      }

      // 仅管理员显示的菜单项
      if (this.hasPermission('management')) {
        pages.push(
          {name: '人员管理', index: '/UserManagement', permission: 'management'}
        )
      }

      return pages
    },
    // 用户角色中文显示
    userRoleText () {
      const roleMap = {
        'admin': '管理员',
        'monitor': '监测员',
        'detector': '检测员'
      }
      return roleMap[this.getUserRole] || ''
    }
  },
  methods: {
    // 登出
    logout () {
      this.$confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 调用登出action
        this.$store.dispatch('user/logout').then(() => {
          // 跳转到登录页
          this.$router.push('/')
          this.$message.success('退出登录成功')
        })
      }).catch(() => {
        // 取消登出
      })
    }
  }
}
</script>

<style scoped>
.logo {
  float: left;
  margin: 2% 3%;
  width: 70px;
  height: 70px;
}

.el-menu {
  border-bottom: none !important;
  background-color: rgba(0, 0, 0, 0.525);
  /* margin-right: 3%; */
  display: flex;
  justify-content: flex-start;
}

.user-info-item {
  margin-left: auto;
  color: #00ff00 !important;
  font-weight: bold;
  text-shadow: 0 0 5px #00ff00;
}

.user-info-item:hover {
  background-color: transparent !important;
}

.el-menu--horizontal > .el-menu-item {
  margin: 2% 0;
  text-align: center;
  line-height: 7vh;
  display: inline-block;
  font-size: 1.5vw;
  color: #dddddd;
  border-bottom: none;
  border-radius: 8px;
}

.el-menu--horizontal > .el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.775);
  color: #4d86ff;
  border-radius: 8px;
}

.el-menu--horizontal > .el-menu-item.is-active {
  border-bottom: none;
  color: #4d86ff;
}
</style>
