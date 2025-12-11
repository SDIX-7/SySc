<template>
  <div class="container">
    <Menu></Menu>
    <div class="title">
      <span>人员管理</span>
    </div>
    <div class="user-management-content">
      <div class="content-wrapper">
        <el-button type="primary" @click="openAddUserDialog" icon="el-icon-plus" class="add-user-btn">添加用户</el-button>
        <el-table :data="userList" border style="width: 100%" class="user-table">
          <el-table-column prop="id" label="用户ID" width="180"></el-table-column>
          <el-table-column prop="name" label="姓名" width="180"></el-table-column>
          <el-table-column prop="role" label="角色" width="180">
            <template slot-scope="scope">
              <el-tag :type="getRoleType(scope.row.role)">{{ getRoleName(scope.row.role) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template slot-scope="scope">
              <el-button type="danger" size="small" @click="deleteUser(scope.row.id)" :disabled="scope.row.id === 'admin'">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 添加用户对话框 -->
      <el-dialog title="添加用户" :visible.sync="addUserDialogVisible" width="500px">
        <el-form :model="newUser" :rules="addUserRules" ref="addUserForm" label-width="100px">
          <el-form-item label="用户ID" prop="id">
            <el-input v-model="newUser.id" placeholder="请输入用户ID"></el-input>
          </el-form-item>
          <el-form-item label="姓名" prop="name">
            <el-input v-model="newUser.name" placeholder="请输入姓名"></el-input>
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input type="password" v-model="newUser.password" placeholder="请输入密码" show-password></el-input>
          </el-form-item>
          <el-form-item label="角色" prop="role">
            <el-select v-model="newUser.role" placeholder="请选择角色">
              <el-option label="检测员" value="detector"></el-option>
              <el-option label="监测员" value="monitor"></el-option>
            </el-select>
          </el-form-item>
        </el-form>
        <span slot="footer" class="dialog-footer">
          <el-button @click="addUserDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="addUser">确定</el-button>
        </span>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import Menu from '../components/Menu.vue'

export default {
  name: 'UserManagement',
  components: {
    Menu
  },
  data () {
    return {
      // 用户列表
      userList: [
        { id: 'admin', name: '管理员', role: 'admin' },
        { id: 'detector1', name: '检测员1', role: 'detector' },
        { id: 'monitor1', name: '监测员1', role: 'monitor' }
      ],
      // 添加用户对话框可见性
      addUserDialogVisible: false,
      // 新用户表单
      newUser: {
        id: '',
        name: '',
        password: '',
        role: 'detector'
      },
      // 添加用户表单规则
      addUserRules: {
        id: [
          { required: true, message: '请输入用户ID', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        name: [
          { required: true, message: '请输入姓名', trigger: 'blur' },
          { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
        ],
        role: [
          { required: true, message: '请选择角色', trigger: 'change' }
        ]
      }
    }
  },
  methods: {
    // 获取角色类型，用于标签样式
    getRoleType (role) {
      switch (role) {
        case 'admin':
          return 'danger'
        case 'monitor':
          return 'warning'
        case 'detector':
          return 'success'
        default:
          return ''
      }
    },
    // 获取角色名称
    getRoleName (role) {
      switch (role) {
        case 'admin':
          return '管理员'
        case 'monitor':
          return '监测员'
        case 'detector':
          return '检测员'
        default:
          return role
      }
    },
    // 打开添加用户对话框
    openAddUserDialog () {
      this.addUserDialogVisible = true
      this.$nextTick(() => {
        this.$refs.addUserForm.resetFields()
      })
    },
    // 添加用户
    addUser () {
      this.$refs.addUserForm.validate((valid) => {
        if (valid) {
          // 检查用户ID是否已存在
          const existingUser = this.userList.find(user => user.id === this.newUser.id)
          if (existingUser) {
            this.$message.error('用户ID已存在')
            return
          }
          // 添加用户
          this.userList.push({
            id: this.newUser.id,
            name: this.newUser.name,
            role: this.newUser.role
          })
          // 关闭对话框
          this.addUserDialogVisible = false
          // 重置表单
          this.$refs.addUserForm.resetFields()
          this.$message.success('用户添加成功')
        }
      })
    },
    // 删除用户
    deleteUser (id) {
      this.$confirm('确定要删除该用户吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 查找用户索引
        const index = this.userList.findIndex(user => user.id === id)
        if (index !== -1) {
          // 删除用户
          this.userList.splice(index, 1)
          this.$message.success('用户删除成功')
        }
      }).catch(() => {
        // 取消删除
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

.user-management-content {
  margin-top: 20px;
  padding: 0 50px;
}

.content-wrapper {
  background-color: rgba(255, 255, 255, 0.9);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.add-user-btn {
  margin-bottom: 20px;
}

.user-table {
  background-color: white;
}
</style>
