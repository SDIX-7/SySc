<template>
  <div>
    <el-menu
      :default-active="$route.path"
      class="el-menu-demo"
      mode="horizontal"
      router>
      <img class="logo" src="../assets/CJLUlogo.jpg" alt=""/>
      <el-menu-item v-for="page in pages"
                    :key="page.index"
                    :index="page.index">
        {{ page.name }}
      </el-menu-item>
    </el-menu>
  </div>
</template>
<script>
export default {
  name: 'Menu',
  data () {
    return {
      pages: [
        {name: '首页', index: '/'},
        {name: '功能介绍', index: '/Detecting'},
        {name: '图像检测', index: '/DetectByImg'},
        {name: '历史记录', index: '/History'},
        {name: '过程控制', index: '/ProcessControl'}
      ]
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
